import React, { useEffect, useState } from 'react';
import { useRecoilValue } from 'recoil';
import { userState } from '../state/atoms';
import { getSessions } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { motion } from 'framer-motion';
import { Clock, EyeOff, Layers, Activity } from 'lucide-react';

export default function Dashboard() {
  const user = useRecoilValue(userState);
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await getSessions();
        setSessions(data);
      } catch (err) {
        console.error("Failed to load sessions");
      }
    }
    loadData();
  }, []);

  const totalTime = sessions.reduce((acc, s) => acc + s.duration_seconds, 0);
  const totalLookAways = sessions.reduce((acc, s) => acc + s.look_away_count, 0);

  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      <header className="flex justify-between items-center mb-10 border-b border-gray-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-gray-400">Welcome back, <span className="text-blue-400">{user?.username}</span></p>
        </div>
        <div className="bg-gray-900 px-4 py-2 rounded-lg border border-gray-800">
            <span className="text-sm text-gray-400">Total Focus Time</span>
            <div className="text-xl font-mono text-green-400">{(totalTime / 60).toFixed(1)}m</div>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <StatCard icon={Clock} title="Sessions" value={sessions.length} color="text-blue-400" />
        <StatCard icon={Activity} title="Avg. Duration" value={`${sessions.length ? (totalTime / sessions.length / 60).toFixed(0) : 0}m`} color="text-green-400" />
        <StatCard icon={EyeOff} title="Look Aways" value={totalLookAways} color="text-yellow-400" />
        <StatCard icon={Layers} title="Focus Score" value="85%" color="text-purple-400" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gray-900 p-6 rounded-2xl border border-gray-800"
        >
          <h3 className="text-xl font-semibold mb-6">Recent Sessions</h3>
          <div className="space-y-4">
            {sessions.slice(0, 5).map((session) => (
              <div key={session.id} className="flex justify-between items-center bg-gray-950 p-4 rounded-xl border border-gray-800/50">
                <div>
                  <p className="font-medium text-white">{session.task || "Untitled Session"}</p>
                  <p className="text-xs text-gray-500">{new Date(session.timestamp).toLocaleDateString()}</p>
                </div>
                <div className="text-right">
                  <p className="text-blue-400 font-mono">{(session.duration_seconds / 60).toFixed(0)}m</p>
                  <p className="text-xs text-gray-500">{session.look_away_count} distractions</p>
                </div>
              </div>
            ))}
            {sessions.length === 0 && <p className="text-gray-500 text-center py-4">No sessions yet.</p>}
          </div>
        </motion.div>

        <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-gray-900 p-6 rounded-2xl border border-gray-800"
        >
          <h3 className="text-xl font-semibold mb-6">Focus Trends</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sessions.slice(-7)}>
                <XAxis dataKey="id" hide />
                <Tooltip 
                    contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', color: '#fff' }}
                    itemStyle={{ color: '#fff' }}
                    labelStyle={{ display: 'none' }}
                />
                <Bar dataKey="duration_seconds" radius={[4, 4, 0, 0]}>
                    {sessions.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#60a5fa' : '#3b82f6'} />
                    ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, title, value, color }) {
    return (
        <motion.div 
            whileHover={{ scale: 1.02 }}
            className="bg-gray-900 p-6 rounded-xl border border-gray-800 flex items-center gap-4"
        >
            <div className={`p-3 rounded-lg bg-gray-950 border border-gray-800 ${color}`}>
                <Icon size={24} />
            </div>
            <div>
                <p className="text-gray-500 text-sm">{title}</p>
                <p className="text-2xl font-bold">{value}</p>
            </div>
        </motion.div>
    );
}
