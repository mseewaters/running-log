// frontend/src/components/__tests__/TargetEditModal.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import TargetEditModal from '../TargetEditModal.vue'
import { targetApi } from '@/services/api'

// Mock the API
vi.mock('@/services/api', () => ({
  targetApi: {
    createTarget: vi.fn(),
    updateTarget: vi.fn(),
    deleteTarget: vi.fn()
  }
}))

describe('TargetEditModal', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // Test 1: Modal renders when open
  it('renders modal when isOpen is true', () => {
    const wrapper = mount(TargetEditModal, {
      props: {
        isOpen: true,
        monthKey: '2025-06',
        monthName: 'June',
        existingTarget: null
      }
    })

    expect(wrapper.find('[data-testid="modal-overlay"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="modal-title"]').text()).toContain('June 2025')
  })

  // Test 2: Modal hidden when closed
  it('does not render modal when isOpen is false', () => {
    const wrapper = mount(TargetEditModal, {
      props: {
        isOpen: false,
        monthKey: '2025-06',
        monthName: 'June',
        existingTarget: null
      }
    })

    expect(wrapper.find('[data-testid="modal-overlay"]').exists()).toBe(false)
  })

  // Test 3: Create new target mode - shows correct buttons
  it('shows create mode buttons when no existing target', () => {
    const wrapper = mount(TargetEditModal, {
      props: {
        isOpen: true,
        monthKey: '2025-06',
        monthName: 'June',
        existingTarget: null
      }
    })

    // Should show Cancel and Save, but no Delete
    expect(wrapper.find('[data-testid="cancel-button"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="save-button"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="delete-button"]').exists()).toBe(false)
  })

  // Test 4: Edit existing target mode - shows all three buttons
  it('shows edit mode buttons when existing target provided', () => {
    const existingTarget = {
      target_id: 'test-id',
      user_id: 'user-id',
      target_type: 'monthly' as const,
      period: '2025-06',
      period_display: 'June 2025',
      distance_km: 100,
      created_at: '2025-06-01T00:00:00Z'
    }

    const wrapper = mount(TargetEditModal, {
      props: {
        isOpen: true,
        monthKey: '2025-06',
        monthName: 'June',
        existingTarget
      }
    })

    // Should show all three buttons
    expect(wrapper.find('[data-testid="delete-button"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="cancel-button"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="save-button"]').exists()).toBe(true)
  })

  // Test 5: Input field pre-populated with existing value
  it('pre-populates input with existing target value', () => {
    const existingTarget = {
      target_id: 'test-id',
      user_id: 'user-id',
      target_type: 'monthly' as const,
      period: '2025-06',
      period_display: 'June 2025',
      distance_km: 100,
      created_at: '2025-06-01T00:00:00Z'
    }

    const wrapper = mount(TargetEditModal, {
      props: {
        isOpen: true,
        monthKey: '2025-06',
        monthName: 'June',
        existingTarget
      }
    })

    const input = wrapper.find('[data-testid="distance-input"]')
    expect(input.element.value).toBe('100')
  })

  // Test 6: Cancel button emits close event
  it('emits close event when cancel is clicked', async () => {
    const wrapper = mount(TargetEditModal, {
      props: {
        isOpen: true,
        monthKey: '2025-06',
        monthName: 'June',
        existingTarget: null
      }
    })

    await wrapper.find('[data-testid="cancel-button"]').trigger('click')

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  // Test 7: Save new target calls API and emits success
  it('creates new target when save is clicked', async () => {
    const mockResponse = {
      target_id: 'new-id',
      user_id: 'user-id',
      target_type: 'monthly' as const,
      period: '2025-06',
      period_display: 'June 2025',
      distance_km: 150,
      created_at: '2025-06-01T00:00:00Z'
    }

    vi.mocked(targetApi.createTarget).mockResolvedValue(mockResponse)

    const wrapper = mount(TargetEditModal, {
      props: {
        isOpen: true,
        monthKey: '2025-06',
        monthName: 'June',
        existingTarget: null
      }
    })

    // Enter a value and save
    await wrapper.find('[data-testid="distance-input"]').setValue('150')
    await wrapper.find('[data-testid="save-button"]').trigger('click')
    await wrapper.vm.$nextTick()

    // Should call API with correct data
    expect(targetApi.createTarget).toHaveBeenCalledWith({
      target_type: 'monthly',
      period: '2025-06',
      distance_km: 150
    })

    // Should emit success event
    expect(wrapper.emitted('success')).toBeTruthy()
  })

  // Test 8: Update existing target calls API correctly
  it('updates existing target when save is clicked', async () => {
    const existingTarget = {
      target_id: 'test-id',
      user_id: 'user-id',
      target_type: 'monthly' as const,
      period: '2025-06',
      period_display: 'June 2025',
      distance_km: 100,
      created_at: '2025-06-01T00:00:00Z'
    }

    const mockResponse = { ...existingTarget, distance_km: 125 }
    vi.mocked(targetApi.updateTarget).mockResolvedValue(mockResponse)

    const wrapper = mount(TargetEditModal, {
      props: {
        isOpen: true,
        monthKey: '2025-06',
        monthName: 'June',
        existingTarget
      }
    })

    // Change the value and save
    await wrapper.find('[data-testid="distance-input"]').setValue('125')
    await wrapper.find('[data-testid="save-button"]').trigger('click')
    await wrapper.vm.$nextTick()

    // Should call update API
    expect(targetApi.updateTarget).toHaveBeenCalledWith('test-id', {
      target_type: 'monthly',
      period: '2025-06',
      distance_km: 125
    })

    expect(wrapper.emitted('success')).toBeTruthy()
  })

  // Test 9: Form validation - empty input
  it('shows validation error for empty input', async () => {
    const wrapper = mount(TargetEditModal, {
      props: {
        isOpen: true,
        monthKey: '2025-06',
        monthName: 'June',
        existingTarget: null
      }
    })

    // Try to save without entering a value
    await wrapper.find('[data-testid="save-button"]').trigger('click')
    await wrapper.vm.$nextTick()

    // Should show validation error
    expect(wrapper.find('[data-testid="validation-error"]').exists()).toBe(true)

    // Should not call API
    expect(targetApi.createTarget).not.toHaveBeenCalled()
  })

  // Test 10: Form validation - invalid input
  it('shows validation error for invalid input', async () => {
    const wrapper = mount(TargetEditModal, {
      props: {
        isOpen: true,
        monthKey: '2025-06',
        monthName: 'June',
        existingTarget: null
      }
    })

    // Enter invalid value and save
    await wrapper.find('[data-testid="distance-input"]').setValue('-10')
    await wrapper.find('[data-testid="save-button"]').trigger('click')
    await wrapper.vm.$nextTick()

    // Should show validation error
    expect(wrapper.find('[data-testid="validation-error"]').exists()).toBe(true)

    // Should not call API
    expect(targetApi.createTarget).not.toHaveBeenCalled()
  })
})
