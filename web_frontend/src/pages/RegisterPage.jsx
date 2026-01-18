import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { register } from '../services/api';
import { motion } from 'framer-motion';
import { UserPlus, ArrowRight } from 'lucide-react';

export default function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await register(username, email, password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please check the backend connection.');
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950 text-white p-4">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md bg-gray-900 p-8 rounded-2xl border border-gray-800 shadow-2xl"
      >
        <div className="text-center mb-8">
          <div className="mx-auto w-12 h-12 bg-purple-600 rounded-xl flex items-center justify-center mb-4">
            <UserPlus className="text-white" size={24} />
          </div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Create Account
          </h2>
          <p className="text-gray-400 mt-2">Join FlowState today</p>
        </div>

        {error && (
          <div className="bg-red-500/10 text-red-500 p-3 rounded-lg mb-6 text-sm text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-gray-950 border border-gray-800 rounded-lg p-3 text-white focus:outline-none focus:border-purple-500 transition-colors"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-gray-950 border border-gray-800 rounded-lg p-3 text-white focus:outline-none focus:border-purple-500 transition-colors"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-gray-950 border border-gray-800 rounded-lg p-3 text-white focus:outline-none focus:border-purple-500 transition-colors"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-3 rounded-lg flex items-center justify-center gap-2 mt-4 transition-colors"
          >
            Sign Up <ArrowRight size={18} />
          </button>
        </form>

        <p className="text-center mt-6 text-gray-500 text-sm">
          Already have an account?{' '}
          <Link to="/" className="text-purple-400 hover:text-purple-300">
            Sign In
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
