
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import Header from "@/components/layout/Header";
import { toast } from "@/hooks/use-toast";
import {
  Play,
  Copy,
  Edit,
  Save,
  RefreshCw,
  Database,
  MessageSquare,
  Code,
  BarChart3,
  CheckCircle,
  Clock,
  Upload,
} from "lucide-react";
import { fetchActiveSchema, generateSQL, listConnections, executeSQL, analyzeResults } from "@/api/query";
// import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";

const Dashboard = () => {
  const [naturalLanguageQuery, setNaturalLanguageQuery] = useState("");
  const [generatedSQL, setGeneratedSQL] = useState("");
  const [editableSQL, setEditableSQL] = useState("");
  const [isEditingSQL, setIsEditingSQL] = useState(false);
  const [queryResults, setQueryResults] = useState<any[]>([]);
  const [naturalLanguageResponse, setNaturalLanguageResponse] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [hasSchema, setHasSchema] = useState(false); // Simulate schema status
  const [schemaName, setSchemaName] = useState<string | null>(null);
  const [connections, setConnections] = useState<any[]>([]);
  const [selectedConnectionId, setSelectedConnectionId] = useState<string>("");

  useEffect(() => {
    async function fetchConnections() {
      try {
        const res = await listConnections();
        setConnections(res.connections || []);
        if (res.connections && res.connections.length > 0) {
          setSelectedConnectionId(res.connections[0].id);
        }
      } catch (e: any) {
        toast({
          title: "Error fetching connections",
          description: e.message,
          variant: "destructive",
        });
      }
    }
    fetchConnections();
  }, []);

  useEffect(() => {
    async function checkSchemaStatus() {
      try {
        const status = await fetchActiveSchema();
        setHasSchema(status.status === "active");
        setSchemaName(status.schema_name || null);
      } catch (e) {
        setHasSchema(false);
        setSchemaName(null);
      }
    }
    checkSchemaStatus();
  }, []);

  // Mock data for demonstration
  const mockResults = [
    { id: 1, customer_name: "Acme Corp", revenue: 125000, quarter: "Q1 2024" },
    { id: 2, customer_name: "TechFlow Inc", revenue: 98000, quarter: "Q1 2024" },
    { id: 3, customer_name: "DataVault Ltd", revenue: 87500, quarter: "Q1 2024" },
    { id: 4, customer_name: "CloudSync", revenue: 76000, quarter: "Q1 2024" },
    { id: 5, customer_name: "NextGen Solutions", revenue: 65000, quarter: "Q1 2024" },
  ];

  const handleGenerateSQL = async () => {
    if (!naturalLanguageQuery.trim()) {
      toast({
        title: "Please enter a query",
        description: "Type your question in natural language to generate SQL.",
        variant: "destructive",
      });
      return;
    }

    setIsGenerating(true);
    
    try {
      // Fetch the most recent active schema
      const schemaStatus = await fetchActiveSchema();
      if (schemaStatus.status !== "active" || !schemaStatus.schema_id) {
        toast({
          title: "No active schema found",
          description: "Please upload a schema before generating SQL.",
          variant: "destructive",
        });
        setIsGenerating(false);
        return;
      }
      const schemaId = schemaStatus.schema_id;

      // Call backend to generate SQL
      const result = await generateSQL(naturalLanguageQuery, schemaId);
      const sql = result.generated_sql;
      setGeneratedSQL(sql);
      setEditableSQL(sql);

      toast({
        title: "SQL generated successfully!",
        description: "Review the query below and execute when ready.",
      });
      
    } catch (error: any) {
      toast({
        title: "Error generating SQL",
        description: error.message || "Please try again or contact support if the issue persists.",
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExecuteSQL = async () => {
    if (!editableSQL.trim()) {
      toast({
        title: "No SQL to execute",
        description: "Please generate or write a SQL query first.",
        variant: "destructive",
      });
      return;
    }
    setIsExecuting(true);
    try {
      // Fetch the most recent active schema
      const schemaStatus = await fetchActiveSchema();
      if (schemaStatus.status !== "active" || !schemaStatus.schema_id) {
        toast({
          title: "No active schema found",
          description: "Please upload a schema before executing SQL.",
          variant: "destructive",
        });
        setIsExecuting(false);
        return;
      }
      const schemaId = schemaStatus.schema_id;
      const result = await executeSQL(editableSQL, schemaId);
      setQueryResults(result.results || []);
      setNaturalLanguageResponse(""); // Clear previous analysis
      toast({
        title: "Query executed successfully!",
        description: `Retrieved ${result.results?.length || 0} rows.`,
      });
      // --- AI Analysis ---
      if (result.results && result.results.length > 0) {
        setIsAnalyzing(true);
        try {
          const analysis = await analyzeResults(result.results, naturalLanguageQuery, editableSQL);
          setNaturalLanguageResponse(analysis.analysis);
        } catch (e: any) {
          setNaturalLanguageResponse("Failed to generate analysis: " + (e.message || "Unknown error"));
        } finally {
          setIsAnalyzing(false);
        }
      }
    } catch (error: any) {
      toast({
        title: "Error executing query",
        description: error.message || "Please check your SQL syntax and try again.",
        variant: "destructive",
      });
    } finally {
      setIsExecuting(false);
    }
  };

  const handleCopySQL = () => {
    navigator.clipboard.writeText(editableSQL);
    toast({
      title: "SQL copied to clipboard",
      description: "The SQL query has been copied to your clipboard.",
    });
  };

  const handleEditSQL = () => {
    setIsEditingSQL(!isEditingSQL);
    if (isEditingSQL) {
      toast({
        title: "SQL changes saved",
        description: "Your SQL modifications have been saved.",
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-professional">
      <Header />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-white">Query Dashboard</h1>
              <p className="text-white/80 mt-1">Transform natural language into powerful SQL queries</p>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant={hasSchema ? "default" : "secondary"} className="px-3 py-1 bg-white/10 text-white border-white/20">
                {hasSchema ? (
                  <>
                    <CheckCircle className="w-4 h-4 mr-1" />
                    Schema Loaded
                    {schemaName && (
                      <span className="ml-2 text-xs text-blue-200">({schemaName})</span>
                    )}
                  </>
                ) : (
                  <>
                    <Clock className="w-4 h-4 mr-1" />
                    No Schema
                  </>
                )}
              </Badge>
              {!hasSchema && (
                <Button variant="outline" size="sm" onClick={() => window.location.href = '/schema-upload'} className="bg-white/10 border-white/20 text-white hover:bg-white/20">
                  <Upload className="w-4 h-4 mr-2" />
                  Upload Schema
                </Button>
              )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Input & SQL */}
          <div className="space-y-6">
            {/* Natural Language Input */}
            <Card className="bg-slate-800/80 border-white/10 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center text-white">
                  <MessageSquare className="mr-2 h-5 w-5" />
                  Natural Language Query
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Textarea
                  placeholder="Ask your question in plain English... 
                  
Examples:
• Show me the top 10 customers by revenue this quarter
• What are the most popular products by sales volume?
• Which regions have the highest growth rate?"
                  value={naturalLanguageQuery}
                  onChange={(e) => setNaturalLanguageQuery(e.target.value)}
                  className="min-h-[120px] mb-4 bg-background/50 border-white/10 text-white placeholder:text-white/60"
                />
                <Button 
                  onClick={handleGenerateSQL} 
                  disabled={isGenerating || !naturalLanguageQuery.trim()}
                  className="w-full bg-slate-700 hover:bg-blue-700 text-white border-white/10"
                >
                  {isGenerating ? (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                      Generating SQL...
                    </>
                  ) : (
                    <>
                      <Play className="mr-2 h-4 w-4" />
                      Generate SQL
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* SQL Display */}
            <Card className="bg-slate-800/80 border-white/10 backdrop-blur-sm">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center text-white">
                    <Code className="mr-2 h-5 w-5" />
                    Generated SQL
                  </CardTitle>
                  {generatedSQL && (
                    <div className="flex space-x-2">
                      <Button variant="outline" size="sm" onClick={handleCopySQL} className="border-white/20 text-white hover:bg-white/10">
                        <Copy className="w-4 h-4" />
                      </Button>
                      <Button variant="outline" size="sm" onClick={handleEditSQL} className="border-white/20 text-white hover:bg-white/10">
                        <Edit className="w-4 h-4 mr-1" />
                        {isEditingSQL ? 'Save' : 'Edit'}
                      </Button>
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {generatedSQL ? (
                  <>
                    <div className="bg-slate-900 rounded-lg p-4 mb-4 border border-white/10">
                      <pre className="text-slate-100 text-sm overflow-x-auto">
                        {isEditingSQL ? (
                          <Textarea
                            value={editableSQL}
                            onChange={(e) => setEditableSQL(e.target.value)}
                            className="bg-transparent border-none text-slate-100 font-mono resize-none min-h-[120px]"
                          />
                        ) : (
                          <code>{editableSQL}</code>
                        )}
                      </pre>
                    </div>
                    {/* <div className="mb-4">
                      <Select value={selectedConnectionId} onValueChange={setSelectedConnectionId}>
                        <SelectTrigger className="w-full">
                          <SelectValue placeholder="Select a database connection" />
                        </SelectTrigger>
                        <SelectContent>
                          {connections.map((conn) => (
                            <SelectItem key={conn.id} value={conn.id}>{conn.name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div> */}
                    <Button 
                      onClick={handleExecuteSQL} 
                      disabled={isExecuting}
                      className="w-full bg-slate-700 hover:bg-blue-700 text-white border-white/10"
                    >
                      {isExecuting ? (
                        <>
                          <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                          Executing Query...
                        </>
                      ) : (
                        <>
                          <Play className="mr-2 h-4 w-4" />
                          Execute Query
                        </>
                      )}
                    </Button>
                  </>
                ) : (
                  <div className="text-center py-12 text-white/60">
                    <Code className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Generated SQL will appear here</p>
                    <p className="text-sm">Enter a natural language query to get started</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Results & Response */}
          <div className="space-y-6">
            {/* Query Results */}
            <Card className="bg-slate-800/80 border-white/10 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center text-white">
                  <Database className="mr-2 h-5 w-5" />
                  Query Results
                </CardTitle>
              </CardHeader>
              <CardContent>
                {queryResults.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-white/10">
                          {Object.keys(queryResults[0]).map((column) => (
                            <th key={column} className="text-left py-3 px-4 font-medium text-white/90 capitalize">
                              {column.replace('_', ' ')}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {queryResults.map((row, index) => (
                          <tr key={index} className="border-b border-white/5 hover:bg-white/5">
                            {Object.values(row).map((value, cellIndex) => (
                              <td key={cellIndex} className="py-3 px-4 text-white/80">
                                {typeof value === 'number' && value > 1000 
                                  ? value.toLocaleString() 
                                  : String(value)
                                }
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-12 text-white/60">
                    <BarChart3 className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Query results will appear here</p>
                    <p className="text-sm">Execute a SQL query to see the data</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Natural Language Response */}
            <Card className="bg-slate-800/80 border-white/10 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center text-white">
                  <MessageSquare className="mr-2 h-5 w-5" />
                  AI Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                {isAnalyzing ? (
                  <div className="text-center py-12 text-white/60">
                    <RefreshCw className="w-12 h-12 mx-auto mb-4 animate-spin opacity-50" />
                    <p>Analyzing results with AI...</p>
                  </div>
                ) : naturalLanguageResponse ? (
                  <div className="prose prose-slate max-w-none">
                    <p className="text-white/90 leading-relaxed">
                      {naturalLanguageResponse}
                    </p>
                  </div>
                ) : (
                  <div className="text-center py-12 text-white/60">
                    <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>AI insights will appear here</p>
                    <p className="text-sm">Execute a query to get natural language analysis</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
