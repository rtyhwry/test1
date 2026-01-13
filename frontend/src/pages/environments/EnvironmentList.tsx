import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Table,
  Button,
  Space,
  Tag,
  Card,
  Modal,
  Form,
  Input,
  Select,
  message,
  Typography,
  Row,
  Col,
  Badge,
} from 'antd'
import {
  PlusOutlined,
  SyncOutlined,
  CloudServerOutlined,
} from '@ant-design/icons'
import { environmentAPI } from '../../services/api'

const { Title } = Typography

const EnvironmentList: React.FC = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [environments, setEnvironments] = useState<any[]>([])
  const [hosts, setHosts] = useState<any[]>([])
  const [devices, setDevices] = useState<any[]>([])
  const [modalVisible, setModalVisible] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [envsRes, hostsRes, devicesRes] = await Promise.all([
        environmentAPI.list(),
        environmentAPI.listHosts(),
        environmentAPI.listDevices(),
      ])
      setEnvironments(envsRes.data.data.items || [])
      setHosts(hostsRes.data.data || [])
      setDevices(devicesRes.data.data || [])
    } catch (error) {
      // Mock data
      setEnvironments([
        {
          id: '1',
          name: 'HIL环境1',
          env_type: 'HIL',
          status: 'idle',
          host: { name: '测试主机1', ip_address: '192.168.1.100' },
          capabilities: ['CAN', 'UDS'],
        },
        {
          id: '2',
          name: 'HIL环境2',
          env_type: 'HIL',
          status: 'busy',
          host: { name: '测试主机2', ip_address: '192.168.1.101' },
          current_task_id: 'task1',
          capabilities: ['CAN', 'UDS', 'DoIP'],
        },
        {
          id: '3',
          name: 'SIL环境1',
          env_type: 'SIL',
          status: 'offline',
          host: { name: '测试主机3', ip_address: '192.168.1.102' },
          capabilities: ['Simulation'],
        },
      ])
      setHosts([
        { id: '1', name: '测试主机1', ip_address: '192.168.1.100', status: 'online' },
        { id: '2', name: '测试主机2', ip_address: '192.168.1.101', status: 'online' },
      ])
      setDevices([
        { id: '1', name: 'VCU-001', device_type: 'VCU', status: 'online' },
        { id: '2', name: 'BMS-001', device_type: 'BMS', status: 'online' },
      ])
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { status: 'success' | 'processing' | 'error' | 'default'; text: string }> = {
      idle: { status: 'success', text: '空闲' },
      busy: { status: 'processing', text: '占用' },
      offline: { status: 'default', text: '离线' },
      maintenance: { status: 'error', text: '维护中' },
      reserved: { status: 'processing', text: '已预约' },
    }
    const config = statusMap[status] || { status: 'default' as const, text: status }
    return <Badge status={config.status} text={config.text} />
  }

  const handleCreate = async (values: any) => {
    try {
      await environmentAPI.create(values)
      message.success('创建成功')
      setModalVisible(false)
      form.resetFields()
      loadData()
    } catch (error) {
      message.error('创建失败')
    }
  }

  const columns = [
    {
      title: '环境名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: any) => (
        <a onClick={() => navigate(`/environments/${record.id}`)}>{name}</a>
      ),
    },
    {
      title: '类型',
      dataIndex: 'env_type',
      key: 'env_type',
      width: 100,
      render: (type: string) => <Tag>{type || '-'}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => getStatusBadge(status),
    },
    {
      title: '主机',
      key: 'host',
      render: (_: any, record: any) => (
        <span>
          {record.host?.name} ({record.host?.ip_address})
        </span>
      ),
    },
    {
      title: '能力标签',
      dataIndex: 'capabilities',
      key: 'capabilities',
      render: (caps: string[]) => (
        <Space size={4}>
          {(caps || []).map((cap) => (
            <Tag key={cap} color="blue">{cap}</Tag>
          ))}
        </Space>
      ),
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
            onClick={() => navigate(`/environments/${record.id}`)}
          >
            详情
          </Button>
          {record.status === 'idle' && (
            <Button type="link" size="small">预约</Button>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Title level={4} style={{ margin: 0 }}>测试环境</Title>
        <Space>
          <Button onClick={loadData} icon={<SyncOutlined />}>刷新</Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setModalVisible(true)}
          >
            创建环境
          </Button>
        </Space>
      </div>

      {/* Summary Cards */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <CloudServerOutlined style={{ fontSize: 32, color: '#1890ff' }} />
              <div style={{ marginTop: 8, fontSize: 24, fontWeight: 'bold' }}>
                {environments.length}
              </div>
              <div style={{ color: '#666' }}>总环境数</div>
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <Badge status="success" />
              <span style={{ fontSize: 24, fontWeight: 'bold', marginLeft: 8 }}>
                {environments.filter(e => e.status === 'idle').length}
              </span>
              <div style={{ color: '#666' }}>空闲</div>
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <Badge status="processing" />
              <span style={{ fontSize: 24, fontWeight: 'bold', marginLeft: 8 }}>
                {environments.filter(e => e.status === 'busy').length}
              </span>
              <div style={{ color: '#666' }}>占用</div>
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <Badge status="default" />
              <span style={{ fontSize: 24, fontWeight: 'bold', marginLeft: 8 }}>
                {environments.filter(e => e.status === 'offline').length}
              </span>
              <div style={{ color: '#666' }}>离线</div>
            </div>
          </Card>
        </Col>
      </Row>

      <Card>
        <Table
          columns={columns}
          dataSource={environments}
          rowKey="id"
          loading={loading}
        />
      </Card>

      {/* Create Modal */}
      <Modal
        title="创建测试环境"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
      >
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item
            name="name"
            label="环境名称"
            rules={[{ required: true, message: '请输入环境名称' }]}
          >
            <Input placeholder="请输入环境名称" />
          </Form.Item>
          <Form.Item name="env_type" label="环境类型">
            <Select placeholder="请选择类型">
              <Select.Option value="HIL">HIL</Select.Option>
              <Select.Option value="SIL">SIL</Select.Option>
              <Select.Option value="实车">实车</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="host_id" label="测试主机">
            <Select placeholder="请选择主机">
              {hosts.map(h => (
                <Select.Option key={h.id} value={h.id}>
                  {h.name} ({h.ip_address})
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={3} placeholder="请输入描述" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default EnvironmentList
