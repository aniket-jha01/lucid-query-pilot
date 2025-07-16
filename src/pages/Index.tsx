
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import { ArrowRight } from "lucide-react";

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-professional">
      <Header />

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900/40 to-slate-800/60"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
          <div className="text-center animate-fade-in-up">
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
              Transform
              <span className="text-blue-400"> Natural Language </span>
              into Powerful SQL
            </h1>
            <p className="text-xl text-slate-300 mb-8 max-w-3xl mx-auto">
              The most advanced AI-powered database query agent for data professionals. 
              Upload your schema, ask questions in plain English, and get instant SQL results.
            </p>
            <div className="flex justify-center">
              <Button size="lg" asChild className="text-lg px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white">
                <Link to="/schema-upload">
                  Get Started
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default Index;
