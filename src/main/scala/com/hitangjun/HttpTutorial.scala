package com.hitangjun

import java.net.URI
import java.util.concurrent.TimeUnit

import org.apache.spark.SparkConf
import org.apache.spark.storage.StorageLevel
import org.apache.spark.streaming.http.HttpInputUtils
import org.apache.spark.streaming.{Seconds, StreamingContext}

import scala.concurrent.duration.FiniteDuration
import com.alibaba.fastjson.{JSON, JSONArray, JSONObject}
object HttpTutorial {

  def main(args: Array[String]) {
    System.setProperty("hadoop.home.dir", "C:\\hihexo\\work\\hadoop-2.7.1")
    // Location of the Spark directory 
    val sparkHome = "c:/hihexo/work/spark-2.2.1-bin-hadoop2.7"
    
    // URL of the Spark cluster
    val sparkUrl = TutorialHelper.getSparkUrl()

    // Location of the required JAR files 
    val jarFile = "target/learn_spark_streaming-1.0.jar"

    // HDFS directory for checkpointing
    val checkpointDir = TutorialHelper.getHdfsUrl() + "/checkpoint/" 

//    val ssc = new StreamingContext(sparkUrl,"Tutorial",Seconds(2),sparkHome,Seq(jarFile))

    val conf = new SparkConf().setMaster("local[2]").setAppName("HttpInputDStream")
    val ssc = new StreamingContext(conf, Seconds(5))
    val url = "http://127.0.0.1:9000/api/weibo/statuses/0"
    val dstream = HttpInputUtils.createStream(ssc, new URI(url),
      FiniteDuration(10, TimeUnit.MILLISECONDS), StorageLevel.MEMORY_AND_DISK_SER_2)

    val json = dstream.map(p => JSON.parseObject(p).getJSONArray("statuses"))
    json.foreachRDD { rdd =>
      rdd.foreach { record =>
        for( i <- 0.to(record.size-1) ) {
          println(record.getJSONObject(i).get("text"))
        }
      }
    }

//        dstream.saveAsTextFiles("/tmp/HttpInputDStream")

    ssc.checkpoint(checkpointDir)
    ssc.start()
    ssc.awaitTermination()
    ssc.stop()
//
//    val result = new File("/tmp/").listFiles.toList.filter(_.getName.startsWith("HttpInputDStream")).flatMap {
//      _.listFiles.toList
//        .filter(_.getName.startsWith("part"))
//        .flatMap(Source.fromFile(_).getLines()
//          .map(_.trim)
//          .filter(!_.isEmpty)
//          .toList)
//    }
//    print(result)
//
//    new File("/tmp/").listFiles.filter(_.getName.startsWith("HttpInputDStream"))
//      .foreach(print(_))
//      .foreach(FileUtils.deleteDirectory(_))

  }
}

