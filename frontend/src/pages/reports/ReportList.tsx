import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Table,
  Button,
  Space,
  Tag,
  Card,
  Progress,
  Typography,
  Row,
  Col,
  Statistic,
} from 'antd'
import {
  SyncOutlined,
  DownloadOutlined,
  FileTextOutlined,
} from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import { reportAPI } from '../../services/api'
import dayjs from 'dayjs'

const { Title } = Typography

const ReportList: React.FC = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [reports, setReports] = useState<any[]>([])
  const [statistics, setStatistics] = useState<any>({})

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [reportsRes, statsRes] = await Promise.all([
        reportAPI.list({ page_size: 20 }),
        reportAPI.getStatistics({ period: 'week' }),
      ])
      setReports(reportsRes.data.data.items || [])
      setStatistics(statsRes.data.data || {})
    } catch (error) {
      // Mock data
      setReports([
        {
          id: '1',
          report_name: 'VCU回归测试报告',
          total_cases: 100,
          passed: 95,
          failed: 3,
          skipped: 2,
          pass_rate: 96.94,
          duration: 3600,
          created_at: new Date().toISOString(),
        },
        {
          id: '2',
          report_name: 'BMS功能测试报告',
          total_cases: 50,
          passed: 48,
          failed: 2,
          skipped: 0,
          pass_rate: 96.0,
          duration: 1800,
          created_at: new Date(Date.now() - 86400000).toISOString(),
        },
      ])
      setStatistics({
        overview: {
          total_executions: 156,
          total_cases: 5000,
          avg_pass_rate: 94.5,
        },
        trend: [
          { date: '01-07', pass_rate: 92.5 },
          { date: '01-08', pass_rate: 94.2 },
          { date: '01-09', pass_rate: 91.8 },
          { date: '01-10', pass_rate: 95.6 },
          { date: '01-11', pass_rate: 93.4 },
          { date: '01-12', pass_rate: 96.1 },
          { date: '01-13', pass_rate: 94.5 },
        ],
      })
    } finally {
      setLoading(false)
    }
  }

  const trendChartOption = {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: (statistics.trend || []).map((d: any) => d.date),
    },
    yAxis: {
      type: 'value',
      min: 80,
      max: 100,
      axisLabel: { formatter: '{value}%' },
    },
    series: [{
      name: '通过率',
      type: 'line',
      data: (statistics.trend || []).map((d: any) => d.pass_rate),
      smooth: true,
      areaStyle: { opacity: 0.3 },
      itemStyle: { color: '#1890ff' },
    }],
  }

  const columns = [
    {
      title: '报告名称',
      dataIndex: 'report_name',
      key: 'report_name',
      render: (name: string, record: any) => (
        <a onClick={() => navigate(`/reports/${record.id}`)}>
          <FileTextOutlined style={{ marginRight: 8 }} />
          {name}
        </a>
      ),
    },
    {
      title: '用例统计',
      key: 'stats',
      width: 200,
      render: (_: any, record: any) => (
        <Space size={4}>
          <Tag color="blue">{record.total_cases}总</Tag>
          <Tag color="green">{record.passed}通过</Tag>
          <Tag color="red">{record.failed}失败</Tag>
        </Space>
      ),
    },
    {
      title: '通过率',
      dataIndex: 'pass_rate',
      key: 'pass_rate',
      width: 150,
      render: (rate: number) => (
        <Progress
          percent={rate}
          size="small"
          status={rate >= 90 ? 'success' : rate >= 70 ? 'normal' : 'exception'}
        />
      ),
    },
    {
      title: '执行时长',
      dataIndex: 'duration',
      key: 'duration',
      width: 100,
      render: (duration: number) => {
        const hours = Math.floor(duration / 3600)
        const minutes = Math.floor((duration % 3600) / 60)
        return hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`
      },
    },
    {
      title: '生成时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (time: string) => dayjs(time).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_: any, record: any) => (
        <Space>
          <Button
            type="link"
            size="small"
            onClick={() => navigate(`/reports/${record.id}`)}
          >
            查看
          </Button>
          <Button
            type="link"
            size="small"
            icon={<DownloadOutlined />}
          >
            导出
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Title level={4} style={{ margin: 0 }}>测试报告</Title>
        <Button onClick={loadData} icon={<SyncOutlined />}>刷新</Button>
      </div>

      {/* Statistics */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总执行次数"
              value={statistics.overview?.total_executions || 0}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总用例数"
              value={statistics.overview?.total_cases || 0}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="平均通过率"
              value={statistics.overview?.avg_pass_rate || 0}
              precision={1}
              suffix="%"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card style={{ height: '100%' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 14, color: '#666', marginBottom: 8 }}>本周趋势</div>
              <Progress
                type="dashboard"
                percent={statistics.overview?.avg_pass_rate || 0}
                size={80}
                strokeColor={{
                  '0%': '#ff4d4f',
                  '100%': '#52c41a',
                }}
              />
            </div>
          </Card>
        </Col>
      </Row>

      {/* Trend Chart */}
      <Card title="通过率趋势" style={{ marginBottom: 16 }}>
        <ReactECharts option={trendChartOption} style={{ height: 250 }} />
      </Card>

      {/* Reports Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={reports}
          rowKey="id"
          loading={loading}
        />
      </Card>
    </div>
  )
}

export default ReportList
