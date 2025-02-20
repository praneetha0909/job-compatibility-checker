import React, { useState } from "react";
import axios from "axios";
import { Container, Form, Button, Alert, Card, ProgressBar, FloatingLabel } from "react-bootstrap";
import { FaUpload, FaCheckCircle, FaExclamationTriangle, FaFileAlt, FaQuestionCircle } from "react-icons/fa";

const UploadResume = () => {
    const [jobDesc, setJobDesc] = useState("");
    const [resume, setResume] = useState(null);
    const [score, setScore] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [helpVisible, setHelpVisible] = useState(false);

    const handleFileChange = (e) => {
        setResume(e.target.files[0]);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setScore(null);
        setError(null);
        setLoading(true);

        if (!jobDesc || !resume) {
            setError("❌ Please enter a job description and upload a resume.");
            setLoading(false);
            return;
        }

        const formData = new FormData();
        formData.append("job_desc", jobDesc);
        formData.append("resume", resume);

        try {
            const response = await axios.post("http://127.0.0.1:5000/upload", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            setScore(response.data.match_score);
        } catch (err) {
            setError("❌ Error uploading file. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="custom-background">
            <Container className="mt-5">
                <Card className="p-4 shadow-lg border-0 rounded-lg custom-card">
                    <h2 className="text-center title-text">
                        <FaFileAlt className="me-2" /> Job Compatibility Checker
                    </h2>

                    <Form onSubmit={handleSubmit}>
                        {/* Job Description Input */}
                        <FloatingLabel controlId="jobDesc" label="📋 Paste Job Description Here:" className="mb-3">
                            <Form.Control
                                as="textarea"
                                rows="8"
                                style={{ height: "220px", resize: "vertical" }}
                                value={jobDesc}
                                onChange={(e) => setJobDesc(e.target.value)}
                                placeholder="Paste job responsibilities and qualifications..."
                            />
                        </FloatingLabel>
                        <small className="text-muted">
                            ⚠️ <strong>Note:</strong> Do not paste company information. Paste only Responsibilities, Qualifications, etc.
                        </small>

                        {/* Resume Upload */}
                        <FloatingLabel controlId="resumeUpload" label="📁 Upload Resume (PDF or DOCX):" className="mt-3">
                            <Form.Control type="file" accept=".pdf,.docx" onChange={handleFileChange} />
                        </FloatingLabel>

                        {/* Check Compatibility Button */}
                        <Button variant="primary" type="submit" className="mt-4 w-100 animated-button">
                            {loading ? "Checking..." : <><FaUpload className="me-2" /> Check Compatibility</>}
                        </Button>
                    </Form>

                    {/* Error Message */}
                    {error && (
                        <Alert variant="danger" className="mt-3 fade-in">
                            <FaExclamationTriangle className="me-2" /> {error}
                        </Alert>
                    )}

                    {/* Match Score */}
                    {score !== null && (
                        <Alert variant={score > 50 ? "success" : "warning"} className="mt-3 fade-in">
                            <FaCheckCircle className="me-2" /> <strong>Match Score:</strong> {score}%
                            <ProgressBar now={score} animated variant={score > 50 ? "success" : "warning"} className="mt-2" />
                        </Alert>
                    )}
                </Card>
            </Container>

            {/* Floating Help Button */}
            <div className="floating-button" onClick={() => setHelpVisible(!helpVisible)}>
                <FaQuestionCircle size={30} />
            </div>

            {/* Help Tooltip */}
            {helpVisible && (
                <div className="help-tooltip">
                    <p>💡 Need help? Upload your resume and paste the job description to get a match score.</p>
                </div>
            )}
        </div>
    );
};

export default UploadResume;
