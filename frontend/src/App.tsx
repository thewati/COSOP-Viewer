import { useState, useRef } from "react";
import { Document, Page, pdfjs } from "react-pdf";

import "react-pdf/dist/Page/TextLayer.css";
import "react-pdf/dist/Page/AnnotationLayer.css";

import axios from "axios";

// pdfjs.GlobalWorkerOptions.workerSrc = new URL(
//   "pdfjs-dist/build/pdf.worker.min.mjs",
//   import.meta.url
// ).toString();

pdfjs.GlobalWorkerOptions.workerSrc =
  "/pdf.worker.min.mjs";

function App() {
  const [partners, setPartners] = useState<any[]>([]);
  const [pdfUrl, setPdfUrl] = useState<string>("");
  const [numPages, setNumPages] = useState<number>(0);
  const pageRefs = useRef<(HTMLDivElement | null)[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedPage, setSelectedPage] =
  useState<number | null>(null);

  const onDocumentLoadSuccess = ({
  numPages,
  }: {
    numPages: number;
  }) => {
    setNumPages(numPages);
  };

  const uploadFile = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];

    if (!file) return;

    // Show PDF in browser
    const localPdfUrl = URL.createObjectURL(file);
    setPdfUrl(localPdfUrl);

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);

      const response = await axios.post(
        "http://127.0.0.1:8000/upload",
        formData
      );

      console.log(response.data);

      // Use backend response
      setPartners(response.data.partners || []);
    } catch (error) {
      console.error(error);
      alert("Only PDF files allowed! Try again with a valid PDF.");
    } finally {
      setLoading(false);
    }
  };

  const goToPage = (page: number) => {

  setSelectedPage(page);

  const targetPage =
    pageRefs.current[page - 1];

  if (targetPage) {

    targetPage.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });

  }
  };

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
      }}
    >
      {/* LEFT PANEL */}
      <div
        style={{
          flex: 2,
          borderRight: "1px solid gray",
          padding: "10px",
        }}
      >
        <h2>COSOP PDF Viewer</h2>

        <input
          type="file"
          accept=".pdf"
          onChange={uploadFile}
        />

        <br />
        <br />

        {pdfUrl && (
          <div
            style={{
              height: "90%",
              overflowY: "scroll",
              border: "1px solid #ccc",
            }}
          >
            <Document
              file={pdfUrl}
              onLoadSuccess={onDocumentLoadSuccess}
            >
              {Array.from(
                new Array(Math.min(numPages, 20)), // use new Array(numPages) for no limit
                (_, index) => (
                  <div
                    key={index}
                    ref={(el) => {
                      pageRefs.current[index] = el;
                    }}
                    style={{
                      marginBottom: "20px",
                      border:
                        selectedPage === index + 1
                          ? "4px solid red"
                          : "none",
                    }}
                  >
                    <Page
                      pageNumber={index + 1}
                      width={800}
                    />
                  </div>
                )
              )}
            </Document>
          </div>
        )}
      </div>

      {/* RIGHT PANEL */}
      <div
        style={{
          flex: 1,
          padding: "10px",
          overflowY: "auto",
        }}
      >
        <h2>Partners</h2>

        {loading && <p>Extracting partners...</p>}

        {!loading && partners.length === 0 && (
          <p>No partners found.</p>
        )}

        {partners.map((partner, index) => (
          <div
            key={index}
            onClick={() => goToPage(partner.page)}
            style={{
              border: "1px solid gray",
              marginBottom: "10px",
              padding: "10px",
              cursor: "pointer",
            }}
          >
            <h3>{partner.name}</h3>
            <p>{partner.category}</p>
            <p>Page: {partner.page}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;