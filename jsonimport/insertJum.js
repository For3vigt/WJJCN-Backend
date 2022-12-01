const { MongoClient, ObjectId } = require("mongodb");
const url = "mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/test";
const client = new MongoClient(url);
const dbName = "wjjcn";

const reader = require("xlsx");

const alg = reader.readFile("./Jumbo.xlsx");
let dataAlg = reader.utils.sheet_to_json(alg.Sheets["Sheet1"]);

const insert = dataAlg.map((data) => {
  return {
    brand:
      data.Brand === "Red Bull"
        ? ObjectId("63762d38f2c01e731408394d")
        : ObjectId("63762d52f2c01e731408394f"),
    retailer: ObjectId("63762a7bf2c01e7314083935"),
    name: data.Title,
    product_url: "",
    product_brand: {
      brand: data.Brand,
      title: data.Title,
      "short description 1": data["Short Description 1 (200k) "],
      "short description 2": data["Short Description 2 (200k) "],
      SEO: [
        data["SEO keywords 1"],
        data["SEO keywords 2"],
        data["SEO keywords 3"],
        data["SEO keywords 4"],
      ],
      "bullit points": [
        data["Product Marketing Bullet Point 1"],
        data["Product Marketing Bullet Point 2"],
        data["Product Marketing Bullet Point 3"],
        data["Product Marketing Bullet Point 4"],
      ],
    },
    history: [
      
    ],
  };
});

async function main() {
  // Use connect method to connect to the server
  await client.connect();
  const db = client.db(dbName);
  const collection = db.collection("products");

  // the following code examples can be pasted here...
  //   await collection.deleteMany({});
  await collection.insertMany(insert);
  return "done";
}

main()
  .then(console.log)
  .catch(console.error)
  .finally(() => client.close());
