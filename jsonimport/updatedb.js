const { MongoClient } = require("mongodb");
const url = "mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/test";
const client = new MongoClient(url);
const dbName = "wjjcn";

// const red = {
//   brand: "Red Bull",
//   retailers: "Albert Heijn",
//   products: [],
// };

// const bull = {
//   brand: "Bullit",
//   retailers: "Albert Heijn",
//   products: [],
// };

async function main() {
  // Use connect method to connect to the server
  await client.connect();
  const db = client.db(dbName);
  const collection = db.collection("products");

  // the following code examples can be pasted here...
  await collection.updateMany({}, { $set: {"product_url": ""} }, {upsert: false})
  return "done";
}

main()
  .then(console.log)
  .catch(console.error)
  .finally(() => client.close());
