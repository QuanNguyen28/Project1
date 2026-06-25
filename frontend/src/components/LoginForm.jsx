import React, { useState } from "react";
import { motion } from "framer-motion";
import NeumorphicCard from "./NeumorphicCard";
import { useAuth } from "../AuthContext";

export default function LoginForm({
  onSubmit: onSubmitProp,
  error: externalError = "",
}) {
  const { login } = useAuth();
  const [username, setUsername] = useState("hr_admin");
  const [password, setPassword] = useState("changeme");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (onSubmitProp) {
        await onSubmitProp(username.trim(), password);
      } else {
        await login(username.trim(), password);
      }
    } catch (err) {
      setError(err?.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-24">
      <NeumorphicCard className="p-8">
        <h1 className="text-2xl font-semibold mb-6">Welcome back</h1>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="label">Username</label>
            <input
              className="input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="hr_admin"
            />
          </div>
          <div>
            <label className="label">Password</label>
            <input
              className="input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••"
            />
          </div>
          {(error || externalError) && (
            <div className="text-red-600 text-sm">{error || externalError}</div>
          )}
          <motion.button
            whileTap={{ scale: 0.98 }}
            disabled={loading}
            className="btn-primary w-full"
          >
            {loading ? "Signing in…" : "Sign in"}
          </motion.button>
        </form>
      </NeumorphicCard>
    </div>
  );
}
