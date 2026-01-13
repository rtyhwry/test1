import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Table,
  Button,
  Space,
  Tag,
  Input,
  Select,
  Card,
  message,
  Popconfirm,
  Typography,
  Row,
  Col,
} from 'antd'
import {
  PlusOutlined,
  SearchOutlined,
  SyncOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  PlayCircleOutlined,
  DeleteOutlined,
  EyeOutlined,
} from '@ant-design/icons'
import { taskAPI } from '../../services/api'
import dayjs from 'dayjs'

const { Title } = Typography

const TaskList: React.FC = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [tasks, setTasks] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [filters, setFilters] = useState({
    status: '',
    keyword: '',
  })

  useEffect(() => {
    loadTasks()
  }, [page, pageSize, filters])

  const loadTasks = async () => {
    setLoading(true)
    try {
      const response = await taskAPI.list({
        page,
        page_size: pageSize,
        status: filters.status || undefined,
      })
      setTasks(response.data.data.items || [])
      setTotal(response.data.data.total || 0)
    } catch (error) {
      console.error('Failed to load tasks:', error)
      // Mock data for demo
      setTasks([
        {
          id: '1',
          name: 'VCU回归测试-V1.2.0',
          status: 'running',
          trigger_type: 'immediate',
          priority: 5,
          source: 'manual',
          created_at: new Date().toISOString(),
          statistics: { total_cases: 100, passed: 45, failed: 2, running: 1, pending: 52 },
        },
        {
          id: '2',
          name: 'BMS功能测试',
          status: 'success',
          trigger_type: 'scheduled',
          priority: 3,
          source: 'alm',
          created_at: new Date(Date.now() - 3600000).toISOString(),
          finished_at: new Date(Date.now() - 1800000).toISOString(),
          statistics: { total_cases: 50, passed: 48, failed: 2, skipped: 0 },
        },
        {
          id: '3',
          name: 'MCU冒烟测试',
          status: 'failed',
          trigger_type: 'cron',
          priority: 2,
          source: 'ci',
          created_at: new Date(Date.now() - 7200000).toISOString(),
          finished_at: new Date(Date.now() - 5400000).toISOString(),
          statistics: { total_cases: 30, passed: 25, failed: 5, skipped: 0 },
        },
      ])
      setTotal(3)
    } finally {
      setLoading(false)
    }
  }

  const handleAction = async (taskId: string, action: string) => {
    try {
      await taskAPI.action(taskId, action)
      message.success(`操作成功`)
      loadTasks()
    } catch (error) {
      message.error('操作失败')
    }
  }

  const handleDelete = async (taskId: string) => {
    try {
      await taskAPI.delete(taskId)
      message.success('删除成功')
      loadTasks()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; icon: React.ReactNode; text: string }> = {
      pending: { color: 'default', icon: <ClockCircleOutlined />, text: '待执行' },
      queued: { color: 'processing', icon: <ClockCircleOutlined />, text: '排队中' },
      preparing: { color: 'processing', icon: <SyncOutlined spin />, text: '准备中' },
      running: { color: 'processing', icon: <SyncOutlined spin />, text: '执行中' },
      success: { color: 'success', icon: <CheckCircleOutlined />, text: '成功' },
      failed: { color: 'error', icon: <CloseCircleOutlined />, text: '失败' },
      cancelled: { color: 'default', icon: <CloseCircleOutlined />, text: '已取消' },
      timeout: { color: 'warning', icon: <ClockCircleOutlined />, text: '超时' },
    }
    const config = statusMap[status] || { color: 'default', icon: null, text: status }
    return (
      <Tag color={config.color} icon={config.icon}>
        {config.text}
      </Tag>
    )
  }

  const getTriggerTag = (type: string) => {
    const typeMap: Record<string, { color: string; text: string }> = {
      immediate: { color: 'blue', text: '立即执行' },
      scheduled: { color: 'orange', text: '定时执行' },
      cron: { color: 'purple', text: '周期执行' },
    }
    const config = typeMap[type] || { color: 'default', text: type }
    return <Tag color={config.color}>{config.text}</Tag>
  }

  const columns = [
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: any) => (
        <a onClick={() => navigate(`/tasks/${record.id}`)}>{name}</a>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '触发方式',
      dataIndex: 'trigger_type',
      key: 'trigger_type',
      width: 120,
      render: (type: string) => getTriggerTag(type),
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      render: (priority: number) => (
        <Tag color={priority <= 3 ? 'red' : priority <= 6 ? 'orange' : 'default'}>
          P{priority}
        </Tag>
      ),
    },
    {
      title: '执行统计',
      key: 'statistics',
      width: 200,
      render: (_: any, record: any) => {
        const stats = record.statistics || {}
        return (
          <Space size={4}>
            <Tag color="blue">{stats.total_cases || 0}总</Tag>
            <Tag color="green">{stats.passed || 0}通过</Tag>
            <Tag color="red">{stats.failed || 0}失败</Tag>
          </Space>
        )
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (time: string) => dayjs(time).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_: any, record: any) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/tasks/${record.id}`)}
          >
            详情
          </Button>
          {['pending', 'queued'].includes(record.status) && (
            <Button
              type="link"
              size="small"
              icon={<PlayCircleOutlined />}
              onClick={() => handleAction(record.id, 'start')}
            >
              执行
            </Button>
          )}
          {record.status === 'running' && (
            <Button
              type="link"
              size="small"
              danger
              onClick={() => handleAction(record.id, 'cancel')}
            >
              取消
            </Button>
          )}
          {!['running'].includes(record.status) && (
            <Popconfirm
              title="确定要删除此任务吗？"
              onConfirm={() => handleDelete(record.id)}
            >
              <Button type="link" size="small" danger icon={<DeleteOutlined />}>
                删除
              </Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Title level={4} style={{ margin: 0 }}>测试任务</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate('/tasks/create')}
        >
          创建任务
        </Button>
      </div>

      <Card style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={8}>
            <Input
              placeholder="搜索任务名称"
              prefix={<SearchOutlined />}
              value={filters.keyword}
              onChange={(e) => setFilters({ ...filters, keyword: e.target.value })}
              allowClear
            />
          </Col>
          <Col span={6}>
            <Select
              placeholder="任务状态"
              value={filters.status}
              onChange={(value) => setFilters({ ...filters, status: value })}
              allowClear
              style={{ width: '100%' }}
            >
              <Select.Option value="pending">待执行</Select.Option>
              <Select.Option value="running">执行中</Select.Option>
              <Select.Option value="success">成功</Select.Option>
              <Select.Option value="failed">失败</Select.Option>
            </Select>
          </Col>
          <Col span={4}>
            <Button onClick={loadTasks} icon={<SyncOutlined />}>
              刷新
            </Button>
          </Col>
        </Row>
      </Card>

      <Card>
        <Table
          columns={columns}
          dataSource={tasks}
          rowKey="id"
          loading={loading}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (p, ps) => {
              setPage(p)
              setPageSize(ps)
            },
          }}
        />
      </Card>
    </div>
  )
}

export default TaskList
