import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

export function QAStatusChart({ passed = 0, review = 0, failed = 0 }) {
  const data = [
    { name: 'Passed', value: passed, color: '#10b981' },
    { name: 'Review', value: review, color: '#f59e0b' },
    { name: 'Failed', value: failed, color: '#ef4444' }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">QA Status Distribution</CardTitle>
      </CardHeader>
      <CardContent className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} cx="50%" cy="50%" innerRadius={70} outerRadius={100} paddingAngle={4} dataKey="value">
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc', borderRadius: '8px' }} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
