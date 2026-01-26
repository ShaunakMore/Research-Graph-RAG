export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req, res) {
  try {
    const HF_BASE = "https://strawhat0304-Research-Graph-RAG-app.hf.space";

    const authHeader = req.headers.authorization;
    if (!authHeader) {
      return res.status(401).json({ detail: "Missing auth header" });
    }

    const path = req.query.path.join("/");

    const headers = {
      Authorization: `Bearer ${process.env.HF_TOKEN}`,
    };

    // Preserve content type if present
    if (req.headers["content-type"]) {
      headers["Content-Type"] = req.headers["content-type"];
    }

    const hfRes = await fetch(`${HF_BASE}/${path}`, {
      method: req.method,
      headers,
      body: req.method !== "GET" ? req : undefined,
      duplex: "half",
    });

    const arrayBuffer = await hfRes.arrayBuffer();

    res.status(hfRes.status);
    res.setHeader(
      "Content-Type",
      hfRes.headers.get("content-type") || "application/json"
    );
    res.send(Buffer.from(arrayBuffer));

  } catch (err) {
    console.error("Proxy error:", err);
    res.status(500).json({ detail: "Proxy error", error: String(err) });
  }
}