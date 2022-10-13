const { MongoClient } = require("mongodb");
const url = "mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/test";
const client = new MongoClient(url);
const dbName = "wjjcn";

const reader = require("xlsx");

const alg = reader.readFile("./Jumbo.xlsx");
let dataAlg = reader.utils.sheet_to_json(alg.Sheets["Sheet1"]);

const insert = dataAlg.map((data) => {
  return {
    brand: data.Brand,
    retailer: "Jumbo",
    product: data.Title,
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
    product_scraped: {
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
  };
});

async function main() {
  // Use connect method to connect to the server
  await client.connect();
  const db = client.db(dbName);
  const collection = db.collection("brand_retailer_product");

  // the following code examples can be pasted here...
  //   await collection.deleteMany({});
  await collection.insertMany(insert);
  return "done";
}

main()
  .then(console.log)
  .catch(console.error)
  .finally(() => client.close());
