
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import {
  ArrowRight,
  Database,
  Zap,
  Shield,
  Users,
  BarChart3,
  Code,
  CheckCircle,
  Upload,
  MessageSquare,
  Play,
} from "lucide-react";

const Index = () => {
  const features = [
    {
      icon: MessageSquare,
      title: "Natural Language Interface",
      description: "Transform complex business questions into SQL queries using plain English",
    },
    {
      icon: Zap,
      title: "Lightning Fast Results",
      description: "Get instant SQL generation and query execution with AI-powered optimization",
    },
    {
      icon: Shield,
      title: "Enterprise Security",
      description: "Bank-grade security with encrypted schema storage and access controls",
    },
    {
      icon: Database,
      title: "Multi-Format Support",
      description: "Upload schemas in JSON, Excel, CSV, SQL DDL, and plain text formats",
    },
    {
      icon: BarChart3,
      title: "Intelligent Analytics",
      description: "Get natural language explanations of your query results and insights",
    },
    {
      icon: Code,
      title: "SQL Editor Integration",
      description: "Review, modify, and optimize generated SQL with our built-in editor",
    },
  ];

  const testimonials = [
    {
      name: "Sarah Chen",
      role: "Senior Data Analyst",
      company: "TechCorp",
      quote: "QueryAgent has revolutionized how we approach data analysis. Complex queries that used to take hours now take minutes.",
    },
    {
      name: "Marcus Rodriguez",
      role: "Business Intelligence Manager",
      company: "DataFlow Inc",
      quote: "The natural language interface makes database querying accessible to our entire team, not just developers.",
    },
    {
      name: "Emily Watson",
      role: "Database Administrator",
      company: "CloudSystems",
      quote: "The SQL generation is remarkably accurate, and the security features give us confidence in enterprise deployment.",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-professional">
      <Header />

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-indigo-100 opacity-60"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
          <div className="text-center animate-fade-in-up">
            <h1 className="text-4xl md:text-6xl font-bold text-slate-900 mb-6">
              Transform
              <span className="text-transparent bg-clip-text bg-gradient-primary"> Natural Language </span>
              into Powerful SQL
            </h1>
            <p className="text-xl text-slate-600 mb-8 max-w-3xl mx-auto">
              The most advanced AI-powered database query agent for data professionals. 
              Upload your schema, ask questions in plain English, and get instant SQL results.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" asChild className="text-lg px-8 py-4">
                <Link to="/dashboard">
                  Start Querying Now
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild className="text-lg px-8 py-4">
                <Link to="/schema-upload">
                  Upload Schema
                  <Upload className="ml-2 h-5 w-5" />
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              Why Choose QueryAgent?
            </h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Built for the modern data stack with enterprise-grade features and intuitive design
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 group">
                <CardContent className="p-8 text-center">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-primary rounded-xl mb-6 group-hover:scale-110 transition-transform duration-300">
                    <feature.icon className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-slate-900 mb-4">{feature.title}</h3>
                  <p className="text-slate-600">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-24 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              Simple, Powerful Workflow
            </h2>
            <p className="text-xl text-slate-600">Get from question to insight in three easy steps</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-100 rounded-full mb-6">
                <Upload className="h-10 w-10 text-primary" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-4">1. Upload Your Schema</h3>
              <p className="text-slate-600">
                Securely upload your database schema in any format. Our system understands JSON, Excel, CSV, SQL DDL, and more.
              </p>
            </div>
            
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-6">
                <MessageSquare className="h-10 w-10 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-4">2. Ask in Plain English</h3>
              <p className="text-slate-600">
                Type your business question naturally. "Show me top customers by revenue" becomes optimized SQL instantly.
              </p>
            </div>
            
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-purple-100 rounded-full mb-6">
                <Play className="h-10 w-10 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-4">3. Get Instant Results</h3>
              <p className="text-slate-600">
                Review the generated SQL, execute queries, and receive natural language summaries of your results.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              Trusted by Data Professionals
            </h2>
            <p className="text-xl text-slate-600">See what industry leaders are saying about QueryAgent</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="border-0 shadow-lg">
                <CardContent className="p-8">
                  <p className="text-slate-700 mb-6 italic">"{testimonial.quote}"</p>
                  <div className="flex items-center">
                    <div className="w-12 h-12 bg-gradient-primary rounded-full flex items-center justify-center text-white font-semibold mr-4">
                      {testimonial.name.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div>
                      <h4 className="font-semibold text-slate-900">{testimonial.name}</h4>
                      <p className="text-slate-600 text-sm">{testimonial.role}</p>
                      <p className="text-slate-500 text-sm">{testimonial.company}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-primary text-white">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Transform Your Data Workflow?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of data professionals who trust QueryAgent for their database querying needs.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="secondary" asChild className="text-lg px-8 py-4">
              <Link to="/dashboard">
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild className="text-lg px-8 py-4 border-white text-white hover:bg-white hover:text-primary">
              <Link to="/schema-upload">
                Upload Schema First
              </Link>
            </Button>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default Index;
