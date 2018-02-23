package com.hitangjun

import org.apache.spark.streaming.twitter.TwitterUtils
import org.apache.spark.streaming.{Seconds, StreamingContext}

object TwitterPopularTags {
  def main(args: Array[String]) {
//    System.setProperty("hadoop.home.dir", "C:\\hihexo\\work\\hadoop-2.7.1")
    // Location of the Spark directory 
    val sparkHome = "c:/hihexo/work/spark-2.2.1-bin-hadoop2.7"
    
    // URL of the Spark cluster
    val sparkUrl = TutorialHelper.getSparkUrl()

    // Location of the required JAR files 
    val jarFile = "target/twitter_streaming-1.0.jar"

    // HDFS directory for checkpointing
    val checkpointDir = TutorialHelper.getHdfsUrl() + "/checkpoint/" 

    // Configure Twitter credentials using twitter.txt
    TutorialHelper.configureTwitterCredentials()
    
    // Your code goes here

    val ssc = new StreamingContext(sparkUrl,"TwitterPopularTags",Seconds(2), System.getenv("SPARK_HOME"),Seq(jarFile))
    val tweets = TwitterUtils.createStream(ssc,None)
    val hashTags = tweets.flatMap(status => status.getText.split(" "))
//   val hashTags = tweets.flatMap(status => status.getText())
    val topCounts60 = hashTags.map((_,1)).reduceByKeyAndWindow(_ + _,Seconds(60))
                    .map{case (topic,count) => (count,topic)}
                    .transform(_.sortByKey(false))
    val topCounts10 = hashTags.map{(_,1)}.reduceByKeyAndWindow(_ + _,Seconds(10))
      .map{case (topic,count) => (count,topic)}
      .transform(_.sortByKey(false))

    topCounts60.foreachRDD(rdd => {
      val topList = rdd.take(5)
      if(rdd.count() > 0){
        println("\nPopular topics in last 60 seconds (%s total):".format(rdd.count))
        topList.foreach{case (count,tag) => println("%s (%s tweets)".format(tag,count))}
        ssc.stop()
      }else{
        println(".....")
      }

    })

    ssc.start()
    ssc.awaitTermination()
  }
}

