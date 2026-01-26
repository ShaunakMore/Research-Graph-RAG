export const config = {
  api: {
    bodyParser: false, // important for file uploads
  },
};

export default async function handler(req, res) {
  try {
    const HF_BASE = "https://strawhat0304-Research-Graph-RAG-app.hf.space";

    const authHeader = req.headers.authorization;
    if (!authHeader) {
      return res.status(401).json({ detail: "Missing auth header" });
    }

    const path = req.query.path.join("/"); // e.g. upload, query

    const hfRes = await fetch(`${HF_BASE}/${path}`, {
      method: req.method,
      headers: {
        Authorization: `Bearer ${process.env.HF_TOKEN}`,
        "Content-Type": req.headers["content-type"] || "application/json",
      },
      body: req.method !== "GET" ? req.body : undefined,
    });

    const data = await hfRes.text();
    res.status(hfRes.status).send(data);

  } catch (err) {
    console.error(err);
    res.status(500).json({ detail: "Proxy error" });
  }
}
