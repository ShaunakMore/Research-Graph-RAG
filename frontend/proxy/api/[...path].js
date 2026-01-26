export default async function handler(req, res) {
  // CORS headers
  res.setHeader("Access-Control-Allow-Origin", "https://research-graph-rag.vercel.app");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");

  // Handle preflight
  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  try {
    const HF_BASE = "https://YOUR_SPACE.hf.space";

    const authHeader = req.headers.authorization;
    if (!authHeader) {
      return res.status(401).json({ detail: "Missing auth header" });
    }

    const path = req.query.path.join("/");

    const headers = {
      Authorization: `Bearer ${process.env.HF_TOKEN}`,
    };

    if (req.headers["content-type"]) {
      headers["Content-Type"] = req.headers["content-type"];
    }

    const hfRes = await fetch(`${HF_BASE}/${path}`, {
      method: req.method,
      headers,
      body: req.method !== "GET" ? req : undefined,
      duplex: "half",
    });

    const buffer = await hfRes.arrayBuffer();

    res.status(hfRes.status);
    res.setHeader("Content-Type", hfRes.headers.get("content-type") || "application/json");
    res.send(Buffer.from(buffer));

  } catch (err) {
    console.error("Proxy error:", err);
    res.status(500).json({ detail: "Proxy error", error: String(err) });
  }
}
