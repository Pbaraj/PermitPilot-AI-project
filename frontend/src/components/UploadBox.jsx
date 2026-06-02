import { useState } from "react";

function UploadBox({ onReview, loading }) {
  const [file, setFile] = useState(null);
  const [outputLanguage, setOutputLanguage] = useState("English");
  const [jurisdiction, setJurisdiction] = useState("general");

  function handleSubmit(event) {
    event.preventDefault();

    if (!file) {
      return;
    }

    onReview({
      file,
      outputLanguage,
      jurisdiction,
    });
  }

  return (
    <form className="card upload-card" onSubmit={handleSubmit}>
      <label>
        Upload permit PDF
        <input
          type="file"
          accept="application/pdf"
          onChange={(event) => setFile(event.target.files?.[0] || null)}
        />
      </label>

      <label>
        Report language
        <select
          value={outputLanguage}
          onChange={(event) => setOutputLanguage(event.target.value)}
        >
          <option>English</option>
          <option>German</option>
          <option>French</option>
          <option>Spanish</option>
          <option>Italian</option>
          <option>Portuguese</option>
          <option>Hindi</option>
          <option>Arabic</option>
          <option>Turkish</option>
          <option>Chinese</option>
        </select>
      </label>

      <label>
        Jurisdiction
        <select
          value={jurisdiction}
          onChange={(event) => setJurisdiction(event.target.value)}
        >
          <option value="general">General</option>
          <option value="germany">Germany / Bavaria</option>
          <option value="munich">Munich / Lokalbaukommission</option>
        </select>
      </label>

      <button type="submit" disabled={!file || loading}>
        {loading ? "Reviewing document..." : "Review document"}
      </button>
    </form>
  );
}

export default UploadBox;