import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function ReviewReasonsChart({ reasons = [] }) {
  // Process top reasons
  const formattedData = reasons.slice(0, 6).map((item) => ({
    name: item.reason.length > 25 ? item.reason.substring(0, 22) + '...' : item.reason,
    count: item.count
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Top Review Reasons & Violations</CardTitle>
      </CardHeader>
      <CardContent className="h-72">
        {formattedData.length === 0 ? (
          <div className="h-full flex items-center justify-center text-textMuted text-sm">
            No violation reasons recorded.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={formattedData} layout="vertical" margin={{ top: 10, right: 30, left: 40, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
              <XAxis type="number" stroke="#94a3b8" />
              <YAxis dataKey="name" type="category" stroke="#94a3b8" tick={{ fontSize: 11 }} width={120} />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc', borderRadius: '8px' }} cursor={{ fill: '#334155', opacity: 0.2 }} />
              <Bar dataKey="count" fill="#f59e0b" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
