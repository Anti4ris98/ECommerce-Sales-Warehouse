import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, sum as _sum, window, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, LongType

print(f"[DEBUG] KAFKA_BOOTSTRAP_SERVERS env var: {os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'NOT SET')}")

# Schema matching the producer's JSON output
schema = StructType([
    StructField("order_id", IntegerType()),
    StructField("user_id", IntegerType()),
    StructField("product_id", IntegerType()),
    StructField("product_title", StringType()),
    StructField("category", StringType()),
    StructField("price", DoubleType()),
    StructField("quantity", IntegerType()),
    StructField("timestamp", DoubleType())
])

def create_spark_session():
    return SparkSession.builder \
        .appName("ECommerceStreaming") \
        .config("spark.sql.shuffle.partitions", "2") \
        .getOrCreate()

def main():
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    
    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")

    # Read from Kafka
    # Note: Requires --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap) \
        .option("subscribe", "ecommerce_events") \
        .option("startingOffsets", "earliest") \
        .load()

    # Parse JSON
    json_df = df.selectExpr("CAST(value AS STRING) as json_string") \
        .select(from_json(col("json_string"), schema).alias("data")) \
        .select("data.*")

    # Basic Cleaning: Deduplicate and drop nulls
    clean_df = json_df.dropDuplicates(["order_id"]).na.drop()

    # Add processing time for windowing (since our timestamp is float/double from python)
    clean_df = clean_df.withColumn("event_time", current_timestamp())

    # Calculate Revenue
    clean_df = clean_df.withColumn("revenue", col("price") * col("quantity"))

    # Aggregation: Revenue by Category per 1 hour window
    windowed_counts = clean_df.groupBy(
        window(col("event_time"), "1 hour"),
        col("category")
    ).agg(
        _sum("revenue").alias("total_revenue")
    )

    # Output to Console for debugging
    query = windowed_counts.writeStream \
        .outputMode("complete") \
        .format("console") \
        .option("truncate", "false") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()
