import { useEffect, useMemo, useState } from 'react'

import {
  getUserOrderDetails,
  getUserOrderItems,
  getUserOrders,
  getUserProfile,
} from '../api/ecommerceApi'

export function useDashboardData() {
  const [dashboard, setDashboard] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const { userId, orderId } = useMemo(() => {
    const params = new URLSearchParams(window.location.search)
    return {
      userId: params.get('user_id') || '1',
      orderId: params.get('order_id') || '555',
    }
  }, [])

  useEffect(() => {
    const controller = new AbortController()

    const loadDashboard = async () => {
      setLoading(true)
      setError('')

      try {
        const [profile, orders] = await Promise.all([
          getUserProfile(userId, controller.signal),
          getUserOrders(userId, controller.signal),
        ])

        let orderDetails = null
        let items = []

        try {
          const [detailsResult, itemsResult] = await Promise.all([
            getUserOrderDetails(userId, orderId, controller.signal),
            getUserOrderItems(userId, orderId, controller.signal),
          ])
          orderDetails = detailsResult
          items = Array.isArray(itemsResult) ? itemsResult : []
        } catch (orderError) {
          if (orderError.name === 'AbortError') {
            throw orderError
          }
        }

        setDashboard({
          user_id: userId,
          order_id: orderId,
          profile,
          orders: Array.isArray(orders) ? orders : [],
          order_details: orderDetails,
          items,
        })
      } catch (err) {
        if (err.name !== 'AbortError') {
          setError('No se pudo conectar con la API.')
          setDashboard(null)
        }
      } finally {
        setLoading(false)
      }
    }

    loadDashboard()

    return () => controller.abort()
  }, [userId, orderId])

  const profile = dashboard?.profile || {
    name: 'Sin datos',
    email: '-',
    addresses: [],
    payments: [],
  }

  const orders = dashboard?.orders || []

  const orderDetails = dashboard?.order_details || {
    order_id: '-',
    date: '-',
    status: '-',
    shipping_address: '-',
    total: 0,
  }

  const items = dashboard?.items || []

  const hasData =
    Boolean(profile?.name && profile.name !== 'Sin datos') ||
    orders.length > 0 ||
    items.length > 0 ||
    (orderDetails.order_id && orderDetails.order_id !== 'ORD#000')

  return {
    userId,
    orderId,
    profile,
    orders,
    orderDetails,
    items,
    loading,
    error,
    hasData,
  }
}
