import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useRecoilValue } from 'recoil';
import { isAuthenticatedState } from './state/atoms';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Dashboard from './pages/Dashboard';

function ProtectedRoute({ children }) {
  const isAuth = useRecoilValue(isAuthenticatedState);
  return isAuth ? children : <Navigate to="/" />;
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;
