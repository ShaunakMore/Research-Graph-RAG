export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req, res) {
  // 1. Set Headers BEFORE anything else
  res.setHeader("Access-Control-Allow-Origin", "https://research-graph-rag.vercel.app");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
  res.setHeader("Access-Control-Allow-Credentials", "true");

  // 2. Immediate Preflight Return
  if (req.method === "OPTIONS") {
    return res.status(204).end(); // 204 No Content is standard for OPTIONS
  }

  try {
    const HF_BASE = "https://YOUR_SPACE.hf.space";
    
    // Safety check for path
    const path = req.query.path ? (Array.isArray(req.query.path) ? req.query.path.join("/") : req.query.path) : "";

    const authHeader = req.headers.authorization;
    if (!authHeader) {
      return res.status(401).json({ detail: "Missing auth header" });
    }

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

    // 3. Ensure CORS headers are also present on the successful response
    res.setHeader("Content-Type", hfRes.headers.get("content-type") || "application/json");
    res.status(hfRes.status).send(Buffer.from(buffer));

  } catch (err) {
    console.error("Proxy error:", err);
    // 4. Ensure CORS headers are present even on Error
    res.status(500).json({ detail: "Proxy error", error: String(err) });
  }
}
