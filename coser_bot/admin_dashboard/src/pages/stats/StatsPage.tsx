/**
 * 数据统计页面
 */
import * as React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { adminApi } from '@/api/admin';

export function StatsPage() {
  const [userGrowth, setUserGrowth] = React.useState([]);
  const [pointsDistribution, setPointsDistribution] = React.useState([]);
  const [verificationRate, setVerificationRate] = React.useState([]);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    const fetchStats = async () => {
      try {
        setIsLoading(true);
        const [growth, points, verification] = await Promise.all([
          adminApi.getUserGrowth(),
          adminApi.getPointsDistribution(),
          adminApi.getVerificationRate()
        ]);
        setUserGrowth(growth);
        setPointsDistribution(points);
        setVerificationRate(verification);
      } catch (err) {
        console.error('加载统计数据失败:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (isLoading) {
    return <div className="p-4">加载中...</div>;
  }

  return (
    <div className="container mx-auto py-10">
      <h1 className="text-2xl font-bold mb-6">数据统计</h1>
      
      <div className="space-y-8">
        {/* 用户增长趋势 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">用户增长趋势</h2>
          <LineChart width={800} height={300} data={userGrowth}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="users" stroke="#8884d8" />
          </LineChart>
        </div>

        {/* 积分分布 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">积分分布</h2>
          <LineChart width={800} height={300} data={pointsDistribution}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="range" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="count" stroke="#82ca9d" />
          </LineChart>
        </div>

        {/* 验证成功率 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">验证成功率</h2>
          <LineChart width={800} height={300} data={verificationRate}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="rate" stroke="#ffc658" />
          </LineChart>
        </div>
      </div>
    </div>
  );
}
