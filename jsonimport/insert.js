const { MongoClient, ObjectId } = require("mongodb");
const url = "mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/test";
const client = new MongoClient(url);
const dbName = "wjjcn";

const reader = require("xlsx");

const alg = reader.readFile("./AH.xlsx");
let dataAlg = reader.utils.sheet_to_json(alg.Sheets["Sheet1"]);

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

const insert = dataAlg.map((data) => {
  return {
    brand:
      data.Opco === "Red Bull"
        ? ObjectId("63762d38f2c01e731408394d")
        : ObjectId("63762d52f2c01e731408394f"),
    retailer: ObjectId("637629daf2c01e7314083933"),
    name: data.Opco + " " + data.Productomschrijving,
    product_url: "",
    product_brand: {
      productomschrijving: data.Productomschrijving,
      inhoud: data.Inhoud,
      Opco: data.Opco,
      omschrijving: data["Omschrijving (max. 200 tekens)"]
        .replace("\r", "")
        .replace("\n", ""),
      USP: [
        data["USP/Bullet 1 (max. 75 tekens)"],
        data["USP/ Bullet 2 (max. 75 tekens)"],
        data["USP/Bullet 3 (max. 75 tekens)"],
        data["USP/Bullet 4 (max. 75 tekens)"],
      ],
    },
    history: [
      {
        scrape_date: "2022-11-10",
        score: 81,
        product_brand: {
          productomschrijving: data.Productomschrijving,
          inhoud: data.Inhoud,
          Opco: data.Opco,
          omschrijving: data["Omschrijving (max. 200 tekens)"]
            .replace("\r", "")
            .replace("\n", ""),
          USP: [
            data["USP/Bullet 1 (max. 75 tekens)"],
            data["USP/ Bullet 2 (max. 75 tekens)"],
            data["USP/Bullet 3 (max. 75 tekens)"],
            data["USP/Bullet 4 (max. 75 tekens)"],
          ],
        },
        product_scraped: {
          productomschrijving: {
            text: "",
            equal_to_scraped: false,
          },
          inhoud: {
            text: "",
            equal_to_scraped: false,
          },
          Opco: {
            text: "",
            equal_to_scraped: false,
          },
          omschrijving: {
            text: "",
            equal_to_scraped: false,
          },
          USP: {
            text: [
              "",
              "",
              "",
              "",
            ],
            equal_to_scraped: false,
          },
        },
      },
    ],
  };
});

async function main() {
  // Use connect method to connect to the server
  await client.connect();
  const db = client.db(dbName);
  const collection = db.collection("products");

  // the following code examples can be pasted here...
  await collection.deleteMany({}); //DELETE ALL OBJECTS IN COLLECTION FIRST.
  await collection.insertMany(insert);
  return "done";
}

main()
  .then(console.log)
  .catch(console.error)
  .finally(() => client.close());
