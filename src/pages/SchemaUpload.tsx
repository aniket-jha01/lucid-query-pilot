
import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import { toast } from "@/hooks/use-toast";
import {
  Upload,
  FileText,
  CheckCircle,
  AlertCircle,
  Database,
  FileJson,
  FileSpreadsheet,
  Code,
  File,
} from "lucide-react";

const SchemaUpload = () => {
  const navigate = useNavigate();
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const supportedFormats = [
    { icon: FileJson, name: "JSON", ext: ".json", description: "Database schema in JSON format" },
    { icon: FileSpreadsheet, name: "Excel", ext: ".xlsx, .xls", description: "Table definitions in spreadsheet" },
    { icon: FileText, name: "CSV", ext: ".csv", description: "Comma-separated schema data" },
    { icon: Code, name: "SQL DDL", ext: ".sql", description: "Data Definition Language scripts" },
    { icon: File, name: "Text", ext: ".txt", description: "Plain text schema descriptions" },
  ];

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileUpload = async (file: File) => {
    setUploadedFile(file);
    setUploadStatus('uploading');
    setUploadProgress(0);

    // Simulate upload progress
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return prev;
        }
        return prev + Math.random() * 15;
      });
    }, 200);

    try {
      // Simulate API call to backend
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setUploadProgress(100);
      setUploadStatus('success');
      
      toast({
        title: "Schema uploaded successfully!",
        description: `${file.name} has been processed and is ready for querying.`,
      });

      // Auto-redirect to dashboard after successful upload
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);

    } catch (error) {
      setUploadStatus('error');
      toast({
        title: "Upload failed",
        description: "There was an error processing your schema file. Please try again.",
        variant: "destructive",
      });
    } finally {
      clearInterval(progressInterval);
    }
  };

  const resetUpload = () => {
    setUploadedFile(null);
    setUploadStatus('idle');
    setUploadProgress(0);
  };

  return (
    <div className="min-h-screen bg-gradient-professional">
      <Header />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-primary rounded-xl mb-6">
            <Database className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-slate-900 mb-4">Upload Your Database Schema</h1>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            Securely upload your database schema to start querying with natural language. 
            We support multiple formats for maximum flexibility.
          </p>
        </div>

        {/* Main Upload Area */}
        <Card className="mb-8">
          <CardContent className="p-8">
            {uploadStatus === 'idle' && (
              <div
                className={`border-2 border-dashed rounded-xl p-12 text-center transition-all duration-200 ${
                  isDragOver 
                    ? 'border-primary bg-blue-50' 
                    : 'border-slate-300 hover:border-slate-400 hover:bg-slate-50'
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <Upload className="h-16 w-16 text-slate-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-slate-900 mb-2">
                  Drop your schema file here
                </h3>
                <p className="text-slate-600 mb-6">
                  or click below to browse and select a file
                </p>
                <input
                  type="file"
                  id="file-upload"
                  className="hidden"
                  accept=".json,.xlsx,.xls,.csv,.sql,.txt"
                  onChange={handleFileSelect}
                />
                <Button asChild size="lg">
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <Upload className="mr-2 h-5 w-5" />
                    Choose File
                  </label>
                </Button>
              </div>
            )}

            {uploadStatus === 'uploading' && uploadedFile && (
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-xl mb-4">
                  <Upload className="h-8 w-8 text-primary animate-pulse" />
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-2">
                  Uploading {uploadedFile.name}
                </h3>
                <p className="text-slate-600 mb-6">Processing your schema file...</p>
                <div className="max-w-md mx-auto">
                  <Progress value={uploadProgress} className="mb-2" />
                  <p className="text-sm text-slate-500">{Math.round(uploadProgress)}% complete</p>
                </div>
              </div>
            )}

            {uploadStatus === 'success' && uploadedFile && (
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-xl mb-4">
                  <CheckCircle className="h-8 w-8 text-green-600" />
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-2">
                  Schema uploaded successfully!
                </h3>
                <p className="text-slate-600 mb-6">
                  {uploadedFile.name} has been processed and validated.
                </p>
                <div className="flex gap-4 justify-center">
                  <Button onClick={() => navigate('/dashboard')}>
                    Start Querying
                  </Button>
                  <Button variant="outline" onClick={resetUpload}>
                    Upload Another
                  </Button>
                </div>
              </div>
            )}

            {uploadStatus === 'error' && (
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-xl mb-4">
                  <AlertCircle className="h-8 w-8 text-red-600" />
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-2">Upload failed</h3>
                <p className="text-slate-600 mb-6">
                  There was an error processing your file. Please check the format and try again.
                </p>
                <Button onClick={resetUpload}>Try Again</Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Supported Formats */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <FileText className="mr-2 h-5 w-5" />
              Supported File Formats
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {supportedFormats.map((format, index) => (
                <div key={index} className="flex items-start space-x-3 p-4 border border-slate-200 rounded-lg">
                  <format.icon className="h-6 w-6 text-primary mt-1" />
                  <div>
                    <h4 className="font-semibold text-slate-900">{format.name}</h4>
                    <p className="text-sm text-slate-500 mb-1">{format.ext}</p>
                    <p className="text-sm text-slate-600">{format.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Instructions */}
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <strong>Schema Format Guidelines:</strong> Ensure your schema includes table names, column definitions, 
            data types, and relationships. For best results, include sample data or field descriptions. 
            All uploads are encrypted and stored securely with enterprise-grade protection.
          </AlertDescription>
        </Alert>
      </div>

      <Footer />
    </div>
  );
};

export default SchemaUpload;
