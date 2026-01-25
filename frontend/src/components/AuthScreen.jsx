import React from 'react';
import { SignIn } from '@clerk/clerk-react';
import { Sparkles, Shield, Zap, Lock } from 'lucide-react';

export default function AuthScreen() {
  return (
    <div className="h-screen bg-linear-to-br from-slate-900 via-purple-900 to-slate-900 flex">
      {/* Left Side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-center items-center p-12 relative overflow-hidden">
        {/* Animated background effect */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-20 left-20 w-72 h-72 bg-purple-500 rounded-full filter blur-3xl animate-pulse"></div>
          <div className="absolute bottom-20 right-20 w-96 h-96 bg-pink-500 rounded-full filter blur-3xl animate-pulse"></div>
        </div>

        <div className="relative z-10 max-w-lg">
          <div className="flex items-center gap-3 mb-8">
            <Sparkles className="w-12 h-12 text-purple-400" />
            <h1 className="text-5xl font-bold text-white">Graph RAG</h1>
          </div>
          
          <p className="text-2xl text-slate-300 mb-12">
            Your intelligent document assistant powered by AI
          </p>

          <div className="space-y-6">
            <div className="flex items-start gap-4">
              <div className="bg-purple-500/20 p-3 rounded-lg">
                <Shield className="w-6 h-6 text-purple-400" />
              </div>
              <div>
                <h3 className="text-white font-semibold mb-1">Secure & Private</h3>
                <p className="text-slate-400 text-sm">Your documents are encrypted and stored securely</p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="bg-pink-500/20 p-3 rounded-lg">
                <Zap className="w-6 h-6 text-pink-400" />
              </div>
              <div>
                <h3 className="text-white font-semibold mb-1">Lightning Fast</h3>
                <p className="text-slate-400 text-sm">Get instant answers from your documents</p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="bg-blue-500/20 p-3 rounded-lg">
                <Lock className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <h3 className="text-white font-semibold mb-1">Enterprise Ready</h3>
                <p className="text-slate-400 text-sm">Built for teams and organizations</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Auth */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="lg:hidden text-center mb-8">
            <div className="flex items-center justify-center gap-2 mb-4">
              <Sparkles className="w-10 h-10 text-purple-400" />
              <h1 className="text-4xl font-bold text-white">Graph RAG</h1>
            </div>
            <p className="text-slate-400">Your intelligent document assistant</p>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-purple-500/20 p-8 shadow-2xl">
            <h2 className="text-2xl font-bold text-white mb-2 text-center">Welcome Back</h2>
            <p className="text-slate-400 text-center mb-8">Sign in to access your documents</p>
            
            <SignIn 
              appearance={{
                elements: {
                  rootBox: "w-full",
                  card: "bg-transparent shadow-none",
                  headerTitle: "hidden",
                  headerSubtitle: "hidden",
                  socialButtonsBlockButton: "bg-slate-700 hover:bg-slate-600 text-white border-slate-600",
                  formButtonPrimary: "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700",
                  footerActionLink: "text-purple-400 hover:text-purple-300",
                  formFieldInput: "bg-slate-700 border-slate-600 text-white",
                  formFieldLabel: "text-slate-300",
                  identityPreviewText: "text-white",
                  identityPreviewEditButton: "text-purple-400",
                }
              }}
            />
          </div>

          <p className="text-center text-slate-500 text-sm mt-6">
            By continuing, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>
      </div>
    </div>
  );
}