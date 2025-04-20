import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import RobotList from '../RobotList.vue'

describe('RobotList', () => {
  it('renders properly with robots', () => {
    const robots = [
      { id: 'robot1', name: 'Test Robot 1', status: 'online' },
      { id: 'robot2', name: 'Test Robot 2', status: 'offline' }
    ]
    
    const wrapper = mount(RobotList, { 
      props: { robots: robots }
    })
    
    expect(wrapper.text()).toContain('Test Robot 1')
    expect(wrapper.text()).toContain('Test Robot 2')
    expect(wrapper.text()).toContain('online')
    expect(wrapper.text()).toContain('offline')
  })

  it('shows empty message when no robots', () => {
    const wrapper = mount(RobotList, { 
      props: { robots: [] }
    })
    
    expect(wrapper.text()).toContain('No robots found')
  })
})