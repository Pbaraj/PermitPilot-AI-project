import { useState } from "react";
import { reviewPermitDocument } from "./api";
import UploadBox from "./components/UploadBox";
import ReportViewer from "./components/ReportViewer";
import "./style.css";

function App() {
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleReview({ file, outputLanguage, jurisdiction }) {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await reviewPermitDocument({
        file,
        outputLanguage,
        jurisdiction,
      });

      setResult(data);
    } catch (err) {
      setError(err.message || "Something went wrong while reviewing the document.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <div className="container">
        <section className="hero">
          <p className="eyebrow">Multilingual Multi-Agent Document Review</p>

          <h1>PermitPilot AI</h1>

          <p>
            Upload an engineering or permit PDF. The assistant extracts project
            information, checks permit completeness, identifies missing items,
            matches Munich regulation references, and generates a readiness
            report.
          </p>
        </section>

        <UploadBox onReview={handleReview} loading={loading} />

        {error && <div className="card error-card">{error}</div>}

        {result && <ReportViewer result={result} />}
      </div>
    </main>
  );
}

export default App;