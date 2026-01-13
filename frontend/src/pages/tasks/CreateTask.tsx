import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Form,
  Input,
  Select,
  Switch,
  InputNumber,
  DatePicker,
  Button,
  Card,
  message,
  Space,
  Typography,
  Divider,
  Row,
  Col,
} from 'antd'
import { ArrowLeftOutlined } from '@ant-design/icons'
import { taskAPI, testSuiteAPI, environmentAPI, projectAPI } from '../../services/api'

const { Title, Text } = Typography
const { TextArea } = Input

const CreateTask: React.FC = () => {
  const navigate = useNavigate()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [projects, setProjects] = useState<any[]>([])
  const [suites, setSuites] = useState<any[]>([])
  const [environments, setEnvironments] = useState<any[]>([])
  const [triggerType, setTriggerType] = useState('immediate')
  const [needUpgrade, setNeedUpgrade] = useState(false)
  const [envStrategy, setEnvStrategy] = useState('auto')

  useEffect(() => {
    loadOptions()
  }, [])

  const loadOptions = async () => {
    try {
      const [projectsRes, suitesRes, envsRes] = await Promise.all([
        projectAPI.list(),
        testSuiteAPI.list(),
        environmentAPI.list(),
      ])
      setProjects(projectsRes.data.data.items || [])
      setSuites(suitesRes.data.data.items || [])
      setEnvironments(envsRes.data.data.items || [])
    } catch (error) {
      // Mock data
      setProjects([
        { id: '1', name: 'VCU项目', code: 'VCU' },
        { id: '2', name: 'BMS项目', code: 'BMS' },
      ])
      setSuites([
        { id: '1', name: 'VCU功能测试套件', case_count: 100 },
        { id: '2', name: 'BMS功能测试套件', case_count: 50 },
      ])
      setEnvironments([
        { id: '1', name: 'HIL环境1', status: 'idle' },
        { id: '2', name: 'HIL环境2', status: 'busy' },
      ])
    }
  }

  const onFinish = async (values: any) => {
    setLoading(true)
    try {
      const payload = {
        name: values.name,
        description: values.description,
        project_id: values.project_id,
        trigger_type: values.trigger_type,
        schedule_time: values.schedule_time?.toISOString(),
        cron_expression: values.cron_expression,
        priority: values.priority,
        need_upgrade: values.need_upgrade,
        version_config: values.need_upgrade ? {
          strategy: values.version_strategy,
          version: values.target_version,
        } : undefined,
        env_config: {
          strategy: values.env_strategy,
          environment_id: values.environment_id,
        },
        test_config: {
          suite_id: values.suite_id,
        },
        execution_config: {
          timeout: values.timeout,
          retry_on_failure: values.retry_on_failure,
          max_retries: values.max_retries,
        },
        notify_config: {
          on_success: values.notify_on_success,
          on_failure: values.notify_on_failure,
          recipients: values.notify_recipients ? values.notify_recipients.split(',') : [],
        },
      }

      await taskAPI.create(payload)
      message.success('任务创建成功')
      navigate('/tasks')
    } catch (error: any) {
      message.error(error.response?.data?.message || '创建失败')
    } finally {
      setLoading(false)
    }
  }

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
          创建测试任务
        </Title>
      </div>

      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
        initialValues={{
          trigger_type: 'immediate',
          priority: 5,
          need_upgrade: false,
          version_strategy: 'latest',
          env_strategy: 'auto',
          timeout: 3600,
          retry_on_failure: false,
          max_retries: 1,
          notify_on_success: true,
          notify_on_failure: true,
        }}
      >
        <Card title="基本信息" style={{ marginBottom: 16 }}>
          <Row gutter={24}>
            <Col span={12}>
              <Form.Item
                name="name"
                label="任务名称"
                rules={[{ required: true, message: '请输入任务名称' }]}
              >
                <Input placeholder="请输入任务名称" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="project_id" label="所属项目">
                <Select placeholder="请选择项目" allowClear>
                  {projects.map((p) => (
                    <Select.Option key={p.id} value={p.id}>
                      {p.name}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="description" label="任务描述">
            <TextArea rows={3} placeholder="请输入任务描述" />
          </Form.Item>
        </Card>

        <Card title="调度配置" style={{ marginBottom: 16 }}>
          <Row gutter={24}>
            <Col span={8}>
              <Form.Item
                name="trigger_type"
                label="触发方式"
                rules={[{ required: true }]}
              >
                <Select onChange={setTriggerType}>
                  <Select.Option value="immediate">立即执行</Select.Option>
                  <Select.Option value="scheduled">定时执行</Select.Option>
                  <Select.Option value="cron">周期执行</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="priority" label="优先级" rules={[{ required: true }]}>
                <InputNumber min={1} max={10} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              {triggerType === 'scheduled' && (
                <Form.Item
                  name="schedule_time"
                  label="执行时间"
                  rules={[{ required: true, message: '请选择执行时间' }]}
                >
                  <DatePicker showTime style={{ width: '100%' }} />
                </Form.Item>
              )}
              {triggerType === 'cron' && (
                <Form.Item
                  name="cron_expression"
                  label="CRON表达式"
                  rules={[{ required: true, message: '请输入CRON表达式' }]}
                >
                  <Input placeholder="0 2 * * *" />
                </Form.Item>
              )}
            </Col>
          </Row>
        </Card>

        <Card title="版本配置" style={{ marginBottom: 16 }}>
          <Row gutter={24}>
            <Col span={8}>
              <Form.Item name="need_upgrade" label="需要升级" valuePropName="checked">
                <Switch onChange={setNeedUpgrade} />
              </Form.Item>
            </Col>
            {needUpgrade && (
              <>
                <Col span={8}>
                  <Form.Item name="version_strategy" label="版本策略">
                    <Select>
                      <Select.Option value="latest">最新版本</Select.Option>
                      <Select.Option value="specific">指定版本</Select.Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="target_version" label="目标版本">
                    <Input placeholder="如: 1.2.0" />
                  </Form.Item>
                </Col>
              </>
            )}
          </Row>
        </Card>

        <Card title="环境配置" style={{ marginBottom: 16 }}>
          <Row gutter={24}>
            <Col span={8}>
              <Form.Item name="env_strategy" label="环境选择策略">
                <Select onChange={setEnvStrategy}>
                  <Select.Option value="auto">自动分配</Select.Option>
                  <Select.Option value="specific">指定环境</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            {envStrategy === 'specific' && (
              <Col span={8}>
                <Form.Item
                  name="environment_id"
                  label="选择环境"
                  rules={[{ required: true, message: '请选择环境' }]}
                >
                  <Select placeholder="请选择环境">
                    {environments.map((e) => (
                      <Select.Option
                        key={e.id}
                        value={e.id}
                        disabled={e.status !== 'idle'}
                      >
                        {e.name} ({e.status === 'idle' ? '空闲' : '占用'})
                      </Select.Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            )}
          </Row>
        </Card>

        <Card title="测试配置" style={{ marginBottom: 16 }}>
          <Row gutter={24}>
            <Col span={12}>
              <Form.Item
                name="suite_id"
                label="测试套件"
                rules={[{ required: true, message: '请选择测试套件' }]}
              >
                <Select placeholder="请选择测试套件">
                  {suites.map((s) => (
                    <Select.Option key={s.id} value={s.id}>
                      {s.name} ({s.case_count}个用例)
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="timeout" label="超时时间(秒)">
                <InputNumber min={60} max={86400} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="retry_on_failure" label="失败重试" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        <Card title="通知配置" style={{ marginBottom: 16 }}>
          <Row gutter={24}>
            <Col span={6}>
              <Form.Item name="notify_on_success" label="成功通知" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="notify_on_failure" label="失败通知" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="notify_recipients" label="通知邮箱">
                <Input placeholder="多个邮箱用逗号分隔" />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        <div style={{ textAlign: 'center' }}>
          <Space size="large">
            <Button onClick={() => navigate('/tasks')}>取消</Button>
            <Button type="primary" htmlType="submit" loading={loading}>
              创建任务
            </Button>
          </Space>
        </div>
      </Form>
    </div>
  )
}

export default CreateTask
