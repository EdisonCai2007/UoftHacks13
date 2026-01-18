import React, { useState } from 'react';
import { useSetRecoilState } from 'recoil';
import { useNavigate, Link } from 'react-router-dom';
import { userState, tokenState } from '../state/atoms';
import { login, getMe } from '../services/api'; // getMe imported
import { motion } from 'framer-motion';
import { LogIn, ArrowRight } from 'lucide-react';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const setUser = useSetRecoilState(userState);
  const setToken = useSetRecoilState(tokenState);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const data = await login(username, password);
      localStorage.setItem('token', data.access_token);
      setToken(data.access_token);
      
      // Fetch user details immediately
      const me = await getMe();
      localStorage.setItem('user', JSON.stringify(me));
      setUser(me);
      
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid credentials');
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
          <div className="mx-auto w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center mb-4">
            <LogIn className="text-white" size={24} />
          </div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Welcome Back
          </h2>
          <p className="text-gray-400 mt-2">Sign in to access your FlowState</p>
        </div>

        {error && (
          <div className="bg-red-500/10 text-red-500 p-3 rounded-lg mb-6 text-sm text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-gray-950 border border-gray-800 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500 transition-colors"
              placeholder="Enter your username"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-gray-950 border border-gray-800 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500 transition-colors"
              placeholder="Enter your password"
            />
          </div>
          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-lg flex items-center justify-center gap-2 transition-colors"
          >
            Sign In <ArrowRight size={18} />
          </button>
        </form>

        <p className="text-center mt-6 text-gray-500 text-sm">
          Don't have an account?{' '}
          <Link to="/register" className="text-blue-400 hover:text-blue-300">
            Create one
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
