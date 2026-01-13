import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card,
  Descriptions,
  Tag,
  Button,
  Space,
  Table,
  Tabs,
  Progress,
  Timeline,
  Typography,
  message,
  Spin,
  Row,
  Col,
  Statistic,
} from 'antd'
import {
  ArrowLeftOutlined,
  PlayCircleOutlined,
  StopOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons'
import { taskAPI } from '../../services/api'
import dayjs from 'dayjs'

const { Title, Text } = Typography
const { TabPane } = Tabs

const TaskDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [task, setTask] = useState<any>(null)
  const [executions, setExecutions] = useState<any[]>([])
  const [caseResults, setCaseResults] = useState<any[]>([])
  const [selectedExecution, setSelectedExecution] = useState<string | null>(null)

  useEffect(() => {
    if (id) {
      loadTask()
      loadExecutions()
    }
  }, [id])

  const loadTask = async () => {
    setLoading(true)
    try {
      const response = await taskAPI.get(id!)
      setTask(response.data.data)
    } catch (error) {
      console.error('Failed to load task:', error)
      // Mock data
      setTask({
        id: id,
        name: 'VCU回归测试-V1.2.0',
        description: 'VCU控制器1.2.0版本完整回归测试',
        status: 'running',
        trigger_type: 'immediate',
        priority: 5,
        need_upgrade: true,
        source: 'manual',
        created_at: new Date().toISOString(),
        started_at: new Date().toISOString(),
        statistics: {
          total_cases: 100,
          passed: 45,
          failed: 2,
          skipped: 0,
          error: 0,
          running: 1,
          pending: 52,
          pass_rate: 95.74,
        },
      })
    } finally {
      setLoading(false)
    }
  }

  const loadExecutions = async () => {
    try {
      const response = await taskAPI.getExecutions(id!)
      setExecutions(response.data.data || [])
    } catch (error) {
      // Mock data
      setExecutions([
        {
          id: 'exec1',
          execution_number: 1,
          status: 'running',
          started_at: new Date().toISOString(),
          total_cases: 100,
          passed_cases: 45,
          failed_cases: 2,
          software_version: '1.2.0',
        },
      ])
    }
  }

  const loadCaseResults = async (executionId: string) => {
    setSelectedExecution(executionId)
    try {
      const response = await taskAPI.getResults(id!, executionId)
      setCaseResults(response.data.data || [])
    } catch (error) {
      // Mock data
      setCaseResults([
        { id: '1', case_name: 'test_power_on', status: 'passed', duration: 1200 },
        { id: '2', case_name: 'test_vehicle_start', status: 'passed', duration: 2500 },
        { id: '3', case_name: 'test_gear_shift', status: 'failed', duration: 1800, error_message: 'Timeout' },
        { id: '4', case_name: 'test_brake_system', status: 'running', duration: 0 },
      ])
    }
  }

  const handleAction = async (action: string) => {
    try {
      await taskAPI.action(id!, action)
      message.success('操作成功')
      loadTask()
      loadExecutions()
    } catch (error) {
      message.error('操作失败')
    }
  }

  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; icon: React.ReactNode; text: string }> = {
      pending: { color: 'default', icon: <ClockCircleOutlined />, text: '待执行' },
      queued: { color: 'processing', icon: <ClockCircleOutlined />, text: '排队中' },
      running: { color: 'processing', icon: <SyncOutlined spin />, text: '执行中' },
      success: { color: 'success', icon: <CheckCircleOutlined />, text: '成功' },
      failed: { color: 'error', icon: <CloseCircleOutlined />, text: '失败' },
      cancelled: { color: 'default', icon: <CloseCircleOutlined />, text: '已取消' },
    }
    const config = statusMap[status] || { color: 'default', icon: null, text: status }
    return (
      <Tag color={config.color} icon={config.icon}>
        {config.text}
      </Tag>
    )
  }

  const resultColumns = [
    {
      title: '用例名称',
      dataIndex: 'case_name',
      key: 'case_name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '耗时',
      dataIndex: 'duration',
      key: 'duration',
      width: 100,
      render: (duration: number) => (duration ? `${duration}ms` : '-'),
    },
    {
      title: '错误信息',
      dataIndex: 'error_message',
      key: 'error_message',
      ellipsis: true,
    },
  ]

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!task) {
    return <div>任务不存在</div>
  }

  const stats = task.statistics || {}
  const progress = stats.total_cases > 0
    ? Math.round(((stats.passed + stats.failed + stats.skipped + stats.error) / stats.total_cases) * 100)
    : 0

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/tasks')}
          style={{ marginRight: 16 }}
        >
          返回
        </Button>
        <Title level={4} style={{ display: 'inline-block', margin: 0 }}>
          {task.name}
        </Title>
        <span style={{ marginLeft: 16 }}>{getStatusTag(task.status)}</span>
      </div>

      {/* Action Buttons */}
      <Card style={{ marginBottom: 16 }}>
        <Space>
          {['pending', 'queued'].includes(task.status) && (
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={() => handleAction('start')}
            >
              开始执行
            </Button>
          )}
          {task.status === 'running' && (
            <Button
              danger
              icon={<StopOutlined />}
              onClick={() => handleAction('cancel')}
            >
              取消执行
            </Button>
          )}
          {['failed', 'cancelled'].includes(task.status) && (
            <Button
              icon={<ReloadOutlined />}
              onClick={() => handleAction('retry')}
            >
              重新执行
            </Button>
          )}
        </Space>
      </Card>

      {/* Statistics */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic title="总用例数" value={stats.total_cases || 0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="通过"
              value={stats.passed || 0}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="失败"
              value={stats.failed || 0}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="通过率"
              value={stats.pass_rate || 0}
              precision={1}
              suffix="%"
              valueStyle={{ color: stats.pass_rate >= 90 ? '#52c41a' : '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Progress */}
      {task.status === 'running' && (
        <Card style={{ marginBottom: 16 }}>
          <Text>执行进度</Text>
          <Progress
            percent={progress}
            status={task.status === 'running' ? 'active' : undefined}
            strokeColor={{
              '0%': '#1890ff',
              '100%': '#52c41a',
            }}
          />
        </Card>
      )}

      {/* Tabs */}
      <Card>
        <Tabs defaultActiveKey="info">
          <TabPane tab="任务信息" key="info">
            <Descriptions column={2} bordered>
              <Descriptions.Item label="任务名称">{task.name}</Descriptions.Item>
              <Descriptions.Item label="状态">{getStatusTag(task.status)}</Descriptions.Item>
              <Descriptions.Item label="触发方式">
                {task.trigger_type === 'immediate' ? '立即执行' : 
                 task.trigger_type === 'scheduled' ? '定时执行' : '周期执行'}
              </Descriptions.Item>
              <Descriptions.Item label="优先级">P{task.priority}</Descriptions.Item>
              <Descriptions.Item label="需要升级">
                {task.need_upgrade ? <Tag color="blue">是</Tag> : <Tag>否</Tag>}
              </Descriptions.Item>
              <Descriptions.Item label="来源">{task.source}</Descriptions.Item>
              <Descriptions.Item label="创建时间">
                {dayjs(task.created_at).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
              <Descriptions.Item label="开始时间">
                {task.started_at ? dayjs(task.started_at).format('YYYY-MM-DD HH:mm:ss') : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="描述" span={2}>
                {task.description || '-'}
              </Descriptions.Item>
            </Descriptions>
          </TabPane>
          
          <TabPane tab="执行记录" key="executions">
            <Table
              dataSource={executions}
              rowKey="id"
              columns={[
                {
                  title: '执行序号',
                  dataIndex: 'execution_number',
                  key: 'execution_number',
                },
                {
                  title: '状态',
                  dataIndex: 'status',
                  key: 'status',
                  render: (status: string) => getStatusTag(status),
                },
                {
                  title: '版本',
                  dataIndex: 'software_version',
                  key: 'software_version',
                },
                {
                  title: '通过/总数',
                  key: 'results',
                  render: (_: any, record: any) => (
                    <span>{record.passed_cases}/{record.total_cases}</span>
                  ),
                },
                {
                  title: '开始时间',
                  dataIndex: 'started_at',
                  key: 'started_at',
                  render: (time: string) => dayjs(time).format('YYYY-MM-DD HH:mm:ss'),
                },
                {
                  title: '操作',
                  key: 'actions',
                  render: (_: any, record: any) => (
                    <Button
                      type="link"
                      onClick={() => loadCaseResults(record.id)}
                    >
                      查看用例结果
                    </Button>
                  ),
                },
              ]}
            />
          </TabPane>
          
          <TabPane tab="用例结果" key="results">
            {selectedExecution ? (
              <Table
                dataSource={caseResults}
                rowKey="id"
                columns={resultColumns}
              />
            ) : (
              <div style={{ textAlign: 'center', padding: 40 }}>
                <Text type="secondary">请在"执行记录"中选择一次执行查看用例结果</Text>
              </div>
            )}
          </TabPane>
        </Tabs>
      </Card>
    </div>
  )
}

export default TaskDetail
