export async function reviewPermitDocument({
  file,
  outputLanguage,
  jurisdiction,
}) {
  const formData = new FormData();

  formData.append("file", file);
  formData.append("output_language", outputLanguage);
  formData.append("jurisdiction", jurisdiction);

  const response = await fetch("http://127.0.0.1:8000/api/review-permit", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to review permit document.");
  }

  return response.json();
}


export async function downloadPdfReport(markdown) {
  const response = await fetch("http://127.0.0.1:8000/api/download-report-pdf", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      filename: "permit-review-report.pdf",
      markdown,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to generate PDF report.");
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = "permit-review-report.pdf";
  link.click();

  URL.revokeObjectURL(url);
}