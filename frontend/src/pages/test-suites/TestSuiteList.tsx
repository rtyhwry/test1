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
} from 'antd'
import {
  PlusOutlined,
  SyncOutlined,
  GithubOutlined,
} from '@ant-design/icons'
import { testSuiteAPI } from '../../services/api'

const { Title } = Typography

const TestSuiteList: React.FC = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [suites, setSuites] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [modalVisible, setModalVisible] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => {
    loadSuites()
  }, [page])

  const loadSuites = async () => {
    setLoading(true)
    try {
      const response = await testSuiteAPI.list({ page, page_size: 20 })
      setSuites(response.data.data.items || [])
      setTotal(response.data.data.total || 0)
    } catch (error) {
      // Mock data
      setSuites([
        {
          id: '1',
          name: 'VCU功能测试套件',
          source: 'gitlab',
          git_repo: 'https://gitlab.example.com/tests/vcu.git',
          framework: 'pytest',
          case_count: 120,
          tags: ['VCU', '功能测试'],
        },
        {
          id: '2',
          name: 'BMS安全测试套件',
          source: 'alm',
          framework: 'robot',
          case_count: 80,
          tags: ['BMS', '安全测试'],
        },
        {
          id: '3',
          name: 'MCU性能测试套件',
          source: 'manual',
          framework: 'pytest',
          case_count: 45,
          tags: ['MCU', '性能测试'],
        },
      ])
      setTotal(3)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (values: any) => {
    try {
      await testSuiteAPI.create(values)
      message.success('创建成功')
      setModalVisible(false)
      form.resetFields()
      loadSuites()
    } catch (error) {
      message.error('创建失败')
    }
  }

  const handleSync = async (suiteId: string) => {
    try {
      await testSuiteAPI.sync(suiteId)
      message.success('同步任务已提交')
    } catch (error) {
      message.error('同步失败')
    }
  }

  const columns = [
    {
      title: '套件名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: any) => (
        <a onClick={() => navigate(`/test-suites/${record.id}`)}>{name}</a>
      ),
    },
    {
      title: '来源',
      dataIndex: 'source',
      key: 'source',
      width: 100,
      render: (source: string) => {
        const sourceMap: Record<string, { color: string; text: string }> = {
          gitlab: { color: 'orange', text: 'GitLab' },
          alm: { color: 'blue', text: 'ALM' },
          manual: { color: 'default', text: '手动' },
        }
        const config = sourceMap[source] || { color: 'default', text: source }
        return <Tag color={config.color}>{config.text}</Tag>
      },
    },
    {
      title: '框架',
      dataIndex: 'framework',
      key: 'framework',
      width: 100,
      render: (fw: string) => fw || '-',
    },
    {
      title: '用例数',
      dataIndex: 'case_count',
      key: 'case_count',
      width: 100,
    },
    {
      title: 'Git仓库',
      dataIndex: 'git_repo',
      key: 'git_repo',
      ellipsis: true,
      render: (repo: string) => repo ? (
        <Space>
          <GithubOutlined />
          <span>{repo}</span>
        </Space>
      ) : '-',
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      render: (tags: string[]) => (
        <Space size={4}>
          {(tags || []).slice(0, 3).map((tag) => (
            <Tag key={tag}>{tag}</Tag>
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
            onClick={() => navigate(`/test-suites/${record.id}`)}
          >
            详情
          </Button>
          {record.source !== 'manual' && (
            <Button
              type="link"
              size="small"
              icon={<SyncOutlined />}
              onClick={() => handleSync(record.id)}
            >
              同步
            </Button>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Title level={4} style={{ margin: 0 }}>测试套件</Title>
        <Space>
          <Button onClick={loadSuites} icon={<SyncOutlined />}>刷新</Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setModalVisible(true)}
          >
            创建套件
          </Button>
        </Space>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={suites}
          rowKey="id"
          loading={loading}
          pagination={{
            current: page,
            total: total,
            onChange: setPage,
          }}
        />
      </Card>

      <Modal
        title="创建测试套件"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
      >
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item
            name="name"
            label="套件名称"
            rules={[{ required: true, message: '请输入套件名称' }]}
          >
            <Input placeholder="请输入套件名称" />
          </Form.Item>
          <Form.Item name="source" label="来源" initialValue="manual">
            <Select>
              <Select.Option value="manual">手动创建</Select.Option>
              <Select.Option value="gitlab">从GitLab导入</Select.Option>
              <Select.Option value="alm">从ALM同步</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="git_repo" label="Git仓库地址">
            <Input placeholder="https://gitlab.example.com/tests/xxx.git" />
          </Form.Item>
          <Form.Item name="git_branch" label="分支" initialValue="main">
            <Input placeholder="main" />
          </Form.Item>
          <Form.Item name="framework" label="测试框架">
            <Select placeholder="请选择框架">
              <Select.Option value="pytest">pytest</Select.Option>
              <Select.Option value="robot">Robot Framework</Select.Option>
              <Select.Option value="custom">自定义</Select.Option>
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

export default TestSuiteList
