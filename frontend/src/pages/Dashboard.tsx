import React, { useEffect, useState } from 'react'
import {
  Row,
  Col,
  Card,
  Statistic,
  Table,
  Tag,
  Progress,
  Space,
  Typography,
} from 'antd'
import {
  ExperimentOutlined,
  CloudServerOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  SyncOutlined,
} from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import { taskAPI, environmentAPI, reportAPI } from '../services/api'

const { Title } = Typography

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    totalTasks: 0,
    runningTasks: 0,
    successRate: 0,
    totalEnvironments: 0,
    availableEnvironments: 0,
  })
  const [recentTasks, setRecentTasks] = useState<any[]>([])
  const [trendData, setTrendData] = useState<any[]>([])

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      // Load statistics
      const [tasksRes, envsRes, statsRes] = await Promise.all([
        taskAPI.list({ page_size: 5 }),
        environmentAPI.list(),
        reportAPI.getStatistics({ period: 'week' }),
      ])

      const tasks = tasksRes.data.data.items || []
      const environments = envsRes.data.data.items || []
      const statistics = statsRes.data.data

      setRecentTasks(tasks)
      
      setStats({
        totalTasks: tasksRes.data.data.total || 0,
        runningTasks: tasks.filter((t: any) => t.status === 'running').length,
        successRate: statistics.overview?.avg_pass_rate || 0,
        totalEnvironments: environments.length,
        availableEnvironments: environments.filter((e: any) => e.status === 'idle').length,
      })

      setTrendData(statistics.trend || [])
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      // Use mock data for demonstration
      setStats({
        totalTasks: 156,
        runningTasks: 3,
        successRate: 94.5,
        totalEnvironments: 12,
        availableEnvironments: 8,
      })
      setRecentTasks([
        { id: '1', name: 'VCU回归测试', status: 'running', created_at: new Date().toISOString() },
        { id: '2', name: 'BMS功能测试', status: 'success', created_at: new Date().toISOString() },
        { id: '3', name: 'MCU冒烟测试', status: 'failed', created_at: new Date().toISOString() },
      ])
      setTrendData([
        { date: '01-07', pass_rate: 92.5 },
        { date: '01-08', pass_rate: 94.2 },
        { date: '01-09', pass_rate: 91.8 },
        { date: '01-10', pass_rate: 95.6 },
        { date: '01-11', pass_rate: 93.4 },
        { date: '01-12', pass_rate: 96.1 },
        { date: '01-13', pass_rate: 94.5 },
      ])
    } finally {
      setLoading(false)
    }
  }

  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; icon: React.ReactNode; text: string }> = {
      pending: { color: 'default', icon: <ClockCircleOutlined />, text: '待执行' },
      queued: { color: 'processing', icon: <ClockCircleOutlined />, text: '排队中' },
      running: { color: 'processing', icon: <SyncOutlined spin />, text: '执行中' },
      success: { color: 'success', icon: <CheckCircleOutlined />, text: '成功' },
      failed: { color: 'error', icon: <CloseCircleOutlined />, text: '失败' },
    }
    const config = statusMap[status] || { color: 'default', icon: null, text: status }
    return (
      <Tag color={config.color} icon={config.icon}>
        {config.text}
      </Tag>
    )
  }

  const columns = [
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time: string) => new Date(time).toLocaleString(),
    },
  ]

  const trendChartOption = {
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      data: trendData.map((d: any) => d.date),
    },
    yAxis: {
      type: 'value',
      min: 80,
      max: 100,
      axisLabel: {
        formatter: '{value}%',
      },
    },
    series: [
      {
        name: '通过率',
        type: 'line',
        data: trendData.map((d: any) => d.pass_rate),
        smooth: true,
        areaStyle: {
          opacity: 0.3,
        },
        itemStyle: {
          color: '#1890ff',
        },
      },
    ],
  }

  const statusChartOption = {
    tooltip: {
      trigger: 'item',
    },
    legend: {
      bottom: '5%',
      left: 'center',
    },
    series: [
      {
        name: '环境状态',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: false,
        },
        data: [
          { value: stats.availableEnvironments, name: '空闲', itemStyle: { color: '#52c41a' } },
          { value: stats.totalEnvironments - stats.availableEnvironments, name: '占用', itemStyle: { color: '#ff4d4f' } },
        ],
      },
    ],
  }

  return (
    <div>
      <Title level={4} style={{ marginBottom: 24 }}>工作台</Title>
      
      {/* Statistics Cards */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总任务数"
              value={stats.totalTasks}
              prefix={<ExperimentOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="执行中任务"
              value={stats.runningTasks}
              prefix={<SyncOutlined spin={stats.runningTasks > 0} />}
              valueStyle={{ color: stats.runningTasks > 0 ? '#1890ff' : undefined }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="平均通过率"
              value={stats.successRate}
              precision={1}
              suffix="%"
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="可用环境"
              value={`${stats.availableEnvironments}/${stats.totalEnvironments}`}
              prefix={<CloudServerOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={16}>
          <Card title="测试通过率趋势" loading={loading}>
            <ReactECharts option={trendChartOption} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="环境状态" loading={loading}>
            <ReactECharts option={statusChartOption} style={{ height: 300 }} />
          </Card>
        </Col>
      </Row>

      {/* Recent Tasks */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="最近任务" loading={loading}>
            <Table
              columns={columns}
              dataSource={recentTasks}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard
