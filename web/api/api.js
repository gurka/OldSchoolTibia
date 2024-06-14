import express from 'express'
import cors from 'cors'
import dotenv from 'dotenv'
import { MongoClient, ObjectId } from 'mongodb'

dotenv.config()

const app = express()
app.use(cors())
const port = 3000

const mongoClient = new MongoClient(process.env.MONGO_URL)
const mongoConnection = await mongoClient.connect()
const mongoDb = mongoConnection.db("oldschooltibia")
const mongoRecordings = mongoDb.collection("recordings")

app.get('/', (req, res) => {
  res.send('Hello World!')
});

app.get("/recording", async (req, res) => {
  const recordings = await mongoRecordings.find({}).project({ filename: 1, version: 1, length_ms: 1 }).limit(50).toArray()
  res.send(recordings).status(200)
});

const getRecording = (id, strings) => {
  let _id
  try {
    _id = ObjectId.createFromHexString(id)
  } catch (e) {
    return null
  }
  return mongoRecordings.findOne({ _id }, { projection: { strings: (strings ? 1 : 0) } })
};

app.get("/recording/:id", async (req, res) => {
  const recording = await getRecording(req.params.id, false)
  if (!recording) {
    res.status(404).send()
    return
  }
  res.send(recording).status(200)
});

app.get("/recording/:id/strings", async (req, res) => {
  const recording = await getRecording(req.params.id, true)
  if (!recording) {
    res.status(404).send()
    return
  }
  res.send(recording).status(200)
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
});