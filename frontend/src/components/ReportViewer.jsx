import { downloadPdfReport } from "../api";

function ReportViewer({ result }) {
  if (!result) {
    return null;
  }

  const checklistResults = result.checklist_results || [];

  const missingRequiredItems = checklistResults.filter(
    (item) => item.required && item.status === "Missing"
  );

  const projectSummary = result.project_summary || {};
  const regulationMatches = projectSummary.regulation_matches || [];
  const ragContext = projectSummary.rag_regulation_context || [];
  const priorityActions = projectSummary.priority_actions || [];

  const aiDecision =
    projectSummary.ai_screening_decision ||
    "AI screening decision not available.";

  const aiSummary =
    projectSummary.ai_reviewer_summary ||
    "AI reviewer summary not available.";

  const llmUsed = projectSummary.llm_used === true;
  const llmProvider = projectSummary.llm_provider || "fallback";
  const llmModel = projectSummary.llm_model || "rule-based reviewer";
  const llmError = projectSummary.llm_error || "";

  function getReviewerMode() {
    if (!llmUsed) {
      return "Fallback rule-based AI reviewer";
    }

    const provider = llmProvider.toLowerCase();

    if (provider === "openrouter") {
      return "OpenRouter LLM reviewer";
    }

    if (provider === "ollama") {
      return "Local Ollama LLM reviewer";
    }

    if (provider === "openai") {
      return "OpenAI LLM reviewer";
    }

    if (provider === "huggingface") {
      return "Hugging Face LLM reviewer";
    }

    return "LLM reviewer";
  }

  function getStatusClass(status) {
    if (status === "Found") {
      return "status found";
    }

    if (status === "Missing") {
      return "status missing";
    }

    return "status unclear";
  }

  function getQualityClass(evidenceQuality) {
    if (evidenceQuality === "Found with evidence") {
      return "quality found-quality";
    }

    if (evidenceQuality === "Mentioned as missing") {
      return "quality negative-quality";
    }

    if (evidenceQuality === "Unclear / conditional") {
      return "quality unclear-quality";
    }

    return "quality notfound-quality";
  }

  function downloadMarkdownReport() {
    const blob = new Blob([result.final_report_markdown], {
      type: "text/markdown",
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "permit-review-report.md";
    link.click();

    URL.revokeObjectURL(url);
  }

  async function handleDownloadPdfReport() {
    try {
      await downloadPdfReport(result.final_report_markdown);
    } catch (error) {
      alert(error.message);
    }
  }

  return (
    <div className="results">
      <div className="card score-card">
        <h2>Permit Readiness</h2>
        <div className="score">{result.readiness_score}%</div>

        <p>
          <strong>Detected language:</strong>{" "}
          {result.detected_languages?.join(", ") || "Unknown"}
        </p>
      </div>

      <div className="card">
        <h2>AI Screening Decision</h2>

        <p>
          <strong>Decision:</strong> {aiDecision}
        </p>

        <p>
          <strong>Reviewer mode:</strong> {getReviewerMode()}
        </p>

        <p>
          <strong>LLM provider:</strong> {llmProvider}
        </p>

        <p>
          <strong>LLM model:</strong> {llmModel}
        </p>

        <p>
          <strong>RAG context:</strong>{" "}
          {ragContext.length > 0
            ? "Munich/Bavaria regulation context retrieved"
            : "No regulation context retrieved"}
        </p>

        {llmError && (
          <div className="small-note error-note">
            <strong>LLM fallback reason:</strong> {llmError}
          </div>
        )}

        <p>{aiSummary}</p>

        <h3>Priority Actions</h3>

        {priorityActions.length > 0 ? (
          <ol>
            {priorityActions.map((action, index) => (
              <li key={index}>{action}</li>
            ))}
          </ol>
        ) : (
          <p>No priority actions generated.</p>
        )}

        <p className="small-note">
          Preliminary AI screening only. Final verification and permit decisions
          must remain with the responsible human authority or qualified reviewer.
        </p>
      </div>

      <div className="card">
        <h2>Translation Notes</h2>

        {result.translation_notes?.length > 0 ? (
          <ul>
            {result.translation_notes.map((note, index) => (
              <li key={index}>{note}</li>
            ))}
          </ul>
        ) : (
          <p>No translation notes available.</p>
        )}
      </div>

      <div className="card">
        <h2>Project Summary</h2>

        <div className="summary-grid">
          <div>
            <strong>Project name</strong>
            <p>{projectSummary.project_name || "Not identified"}</p>
          </div>

          <div>
            <strong>Project address</strong>
            <p>{projectSummary.project_address || "Not identified"}</p>
          </div>

          <div>
            <strong>Applicant / Client</strong>
            <p>{projectSummary.applicant || "Not identified"}</p>
          </div>

          <div>
            <strong>Building type</strong>
            <p>{projectSummary.building_type || "Not identified"}</p>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>Missing Required Items</h2>

        {missingRequiredItems.length > 0 ? (
          <ul>
            {missingRequiredItems.map((item) => (
              <li key={item.id}>{item.requirement}</li>
            ))}
          </ul>
        ) : (
          <p>No required items are missing.</p>
        )}
      </div>

      <div className="card">
        <h2>Checklist Results</h2>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Requirement</th>
                <th>Status</th>
                <th>Required</th>
                <th>Evidence Quality</th>
                <th>Pages</th>
                <th>Evidence</th>
              </tr>
            </thead>

            <tbody>
              {checklistResults.map((item) => (
                <tr key={item.id}>
                  <td>{item.requirement}</td>

                  <td>
                    <span className={getStatusClass(item.status)}>
                      {item.status}
                    </span>
                  </td>

                  <td>{item.required ? "Yes" : "No"}</td>

                  <td>
                    <span className={getQualityClass(item.evidence_quality)}>
                      {item.evidence_quality || "Not found"}
                    </span>
                  </td>

                  <td>
                    {item.page_references?.length > 0
                      ? item.page_references.join(", ")
                      : "-"}
                  </td>

                  <td>
                    {item.evidence?.length > 0 ? (
                      <ul className="evidence-list">
                        {item.evidence.map((evidence, index) => (
                          <li key={index}>{evidence}</li>
                        ))}
                      </ul>
                    ) : (
                      "-"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card">
        <h2>Munich Regulation Matching</h2>

        {regulationMatches.length > 0 ? (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Requirement</th>
                  <th>Status</th>
                  <th>Reference</th>
                  <th>Regulation Note</th>
                  <th>Severity</th>
                </tr>
              </thead>

              <tbody>
                {regulationMatches.map((match, index) => (
                  <tr key={`${match.requirement_id}-${index}`}>
                    <td>{match.requirement}</td>

                    <td>
                      <span className={getStatusClass(match.status)}>
                        {match.status}
                      </span>
                    </td>

                    <td>{match.reference || "-"}</td>
                    <td>{match.rule_summary || "-"}</td>
                    <td>{match.severity || "Medium"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>
            No Munich regulation matches available. Select Munich /
            Lokalbaukommission jurisdiction to enable this section.
          </p>
        )}
      </div>

      <div className="card">
        <h2>Retrieved Munich Regulation Context</h2>

        {ragContext.length > 0 ? (
          <div className="rag-context-list">
            {ragContext.map((chunk, index) => (
              <div className="rag-context-item" key={`${chunk.id}-${index}`}>
                <h3>
                  {index + 1}. {chunk.title || "Untitled retrieved context"}
                </h3>

                <p>
                  <strong>Source:</strong> {chunk.source || "-"}
                </p>

                <p>
                  <strong>Relevance score:</strong> {chunk.score ?? "-"}
                </p>

                <p>
                  <strong>Matched query:</strong> {chunk.matched_query || "-"}
                </p>

                <p>
                  <strong>Retrieved context:</strong> {chunk.text || "-"}
                </p>
              </div>
            ))}

            <p className="small-note">
              Retrieved snippets support AI-assisted screening. They do not
              replace official legal text or human review.
            </p>
          </div>
        ) : (
          <p>No RAG regulation context retrieved for this review.</p>
        )}
      </div>

      <div className="card">
        <h2>Risk Analysis</h2>

        {result.risks?.length > 0 ? (
          <div className="risk-list">
            {result.risks.map((risk, index) => (
              <div className="risk-item" key={index}>
                <h3>
                  {risk.severity}: {risk.title}
                </h3>

                <p>{risk.explanation}</p>

                <p>
                  <strong>Recommendation:</strong> {risk.recommendation}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p>No major risks detected.</p>
        )}
      </div>

      <div className="card">
        <h2>Reviewer Notes</h2>

        {result.reviewer_notes?.length > 0 ? (
          <ul>
            {result.reviewer_notes.map((note, index) => (
              <li key={index}>{note}</li>
            ))}
          </ul>
        ) : (
          <p>No reviewer notes available.</p>
        )}
      </div>

      <div className="card">
        <h2>Final Report</h2>

        <div className="report-actions">
          <button className="download-button" onClick={downloadMarkdownReport}>
            Download Markdown Report
          </button>

          <button
            className="download-button secondary"
            onClick={handleDownloadPdfReport}
          >
            Download PDF Report
          </button>
        </div>

        <pre>{result.final_report_markdown}</pre>
      </div>
    </div>
  );
}

export default ReportViewer;