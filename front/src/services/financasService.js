import api from '@/services/APIService';
import { PAGE_SIZE } from '@/constants/pagination';

const financasService = {

  // =========================
  // --- CATEGORIAS ---
  // =========================
  dashboard: {
    getDashboard: async () => {
      const response = await api.get('/financas/dashboard/');
      return response.data;
    },
  },
  categorias: {

    getAll: async (params = {}) => {
      const response = await api.get('/financas/categorias/', { params });
      return response.data;
    },

    getAllPaginated: async (params = {}) => {
      const { page = 1, order = {}, filter = {} } = params;

      const queryParams = new URLSearchParams();
      queryParams.append('page', page);

      // Ordenação
      if (order.field) {
        const fieldMap = {
          nome: 'nome',
          tipo: 'tipo',
          descricao: 'descricao',
          icone: 'icone',
          created_at: 'created_at',
          last_updated: 'last_updated',
        };

        const backendField = fieldMap[order.field] || order.field;

        queryParams.append('order_field', backendField);
        queryParams.append('order_direction', order.order || 'asc');
      }

      // Filtros
      Object.keys(filter).forEach(key => {
        if (filter[key]) {
          queryParams.append(key, filter[key]);
        }
      });

      const response = await api.get(`/financas/categorias/?${queryParams.toString()}`);

      const results = response.data.results || [];
      const perPage = response.data.page_size || 10;
      const total = response.data.count || 0;

      return {
        data: results,
        page,
        pageSize: perPage,
        total,
        pages: Math.ceil(total / perPage),
      };
    },

    getById: async (id) => {
      const response = await api.get(`/financas/categorias/${id}/`);
      return response.data;
    },

    create: async (data) => {
      const response = await api.post('/financas/categorias/', data);
      return response.data;
    },

    update: async (id, data) => {
      const response = await api.put(`/financas/categorias/${id}/`, data);
      return response.data;
    },

    delete: async (id) => {
      await api.delete(`/financas/categorias/${id}/`);
    },
  },

  // =========================
  // --- MOVIMENTAÇÕES ---
  // =========================
  movimentacoes: {

    getAll: async (params = {}) => {
      const response = await api.get('/financas/movimentacoes/', { params });
      return response.data;
    },

    /**
     * Lista paginada (page size fixo = PAGE_SIZE da app, alinhado ao Django).
     * @param {number} page - Página (1-based)
     * @param {object} params - Filtros (ex: { tipo: 'E' })
     * @returns {{ data: array, total: number }}
     */
    getPage: async (page = 1, params = {}) => {
      const response = await api.get('/financas/movimentacoes/', {
        params: { ...params, page }
      });
      const body = response.data;
      return {
        data: body.results || [],
        total: body.count ?? 0
      };
    },

    getAllPaginated: async (params = {}) => {
      const { page = 1, order = {}, filter = {} } = params;

      const queryParams = new URLSearchParams();
      queryParams.append('page', page);

      // Ordenação
      if (order.field) {
        const fieldMap = {
          valor: 'valor',
          data: 'data',
          tipo: 'tipo',
          categoria: 'categoria',
          created_at: 'created_at',
        };

        const backendField = fieldMap[order.field] || order.field;

        queryParams.append('order_field', backendField);
        queryParams.append('order_direction', order.order || 'asc');
      }

      // Filtros
      Object.keys(filter).forEach(key => {
        if (filter[key]) {
          queryParams.append(key, filter[key]);
        }
      });

      const response = await api.get(`/financas/movimentacoes/?${queryParams.toString()}`);

      const results = response.data.results || [];
      const perPage = response.data.page_size ?? PAGE_SIZE;
      const total = response.data.count || 0;

      return {
        data: results,
        page,
        pageSize: perPage,
        total,
        pages: Math.ceil(total / perPage),
      };
    },

    getById: async (id) => {
      const response = await api.get(`/financas/movimentacoes/${id}/`);
      return response.data;
    },

    create: async (data) => {
      const response = await api.post('/financas/movimentacoes/', data);
      return response.data;
    },

    update: async (id, data) => {
      const response = await api.put(`/financas/movimentacoes/${id}/`, data);
      return response.data;
    },

    delete: async (id) => {
      await api.delete(`/financas/movimentacoes/${id}/`);
    },
  },

  // =========================
  // --- MOVIMENTAÇÕES RECORRENTES ---
  // =========================
  movimentacoesRecorrentes: {

    getAll: async () => {
      const response = await api.get('/financas/movimentacoes-recorrentes/');
      return response.data;
    },

    getAllPaginated: async (params = {}) => {
      const { page = 1, order = {}, filter = {} } = params;

      const queryParams = new URLSearchParams();
      queryParams.append('page', page);

      // Ordenação
      if (order.field) {
        const fieldMap = {
          valor: 'valor',
          tipo: 'tipo',
          frequencia: 'frequencia',
          data_inicio: 'data_inicio',
          data_fim: 'data_fim',
          ativa: 'ativa',
        };

        const backendField = fieldMap[order.field] || order.field;

        queryParams.append('order_field', backendField);
        queryParams.append('order_direction', order.order || 'asc');
      }

      // Filtros
      Object.keys(filter).forEach(key => {
        if (filter[key]) {
          queryParams.append(key, filter[key]);
        }
      });

      const response = await api.get(`/financas/movimentacoes-recorrentes/?${queryParams.toString()}`);

      const results = response.data.results || [];
      const perPage = response.data.page_size || 10;
      const total = response.data.count || 0;

      return {
        data: results,
        page,
        pageSize: perPage,
        total,
        pages: Math.ceil(total / perPage),
      };
    },

    getById: async (id) => {
      const response = await api.get(`/financas/movimentacoes-recorrentes/${id}/`);
      return response.data;
    },

    create: async (data) => {
      const response = await api.post('/financas/movimentacoes-recorrentes/', data);
      return response.data;
    },

    update: async (id, data) => {
      const response = await api.put(`/financas/movimentacoes-recorrentes/${id}/`, data);
      return response.data;
    },

    delete: async (id) => {
      await api.delete(`/financas/movimentacoes-recorrentes/${id}/`);
    },
  },

  // =========================
  // --- METAS ---
  // =========================
  metas: {
    getAll: async () => {
      const response = await api.get('/financas/metas/');
      return response.data;
    },

    getById: async (id) => {
      const response = await api.get(`/financas/metas/${id}/`);
      return response.data;
    },

    create: async (data) => {
      const response = await api.post('/financas/metas/', data);
      return response.data;
    },

    update: async (id, data) => {
      const response = await api.put(`/financas/metas/${id}/`, data);
      return response.data;
    },

    delete: async (id) => {
      await api.delete(`/financas/metas/${id}/`);
    },
  },

  // =========================
  // --- CONSOLIDADOS MENSAIS ---
  // =========================
  consolidadosMensais: {
    getAll: async () => {
      const response = await api.get('/financas/consolidados-mensais/');
      return response.data;
    },

    getById: async (id) => {
      const response = await api.get(`/financas/consolidados-mensais/${id}/`);
      return response.data;
    },

    create: async (data) => {
      const response = await api.post('/financas/consolidados-mensais/', data);
      return response.data;
    },

    update: async (id, data) => {
      const response = await api.put(`/financas/consolidados-mensais/${id}/`, data);
      return response.data;
    },

    delete: async (id) => {
      await api.delete(`/financas/consolidados-mensais/${id}/`);
    },
  },

  // =========================
  // --- ICONE ---
  // =========================
  icone: {
    getAll: async () => {
      const response = await api.get('/financas/icone/');
      return response.data;
    },

    getById: async (id) => {
      const response = await api.get(`/financas/icone/${id}/`);
      return response.data;
    },

    create: async (data) => {
      const response = await api.post('/financas/icone/', data);
      return response.data;
    },

    update: async (id, data) => {
      const response = await api.put(`/financas/icone/${id}/`, data);
      return response.data;
    },

    delete: async (id) => {
      await api.delete(`/financas/icone/${id}/`);
    },
  },

  // =========================
  // --- RESERVAS ---
  // =========================
  reservas: {
    getAll: async () => {
      const response = await api.get('/financas/reservas/');
      return response.data;
    },

    getById: async (id) => {
      const response = await api.get(`/financas/reservas/${id}/`);
      return response.data;
    },

    create: async (data) => {
      const response = await api.post('/financas/reservas/', data);
      return response.data;
    },

    update: async (id, data) => {
      const response = await api.put(`/financas/reservas/${id}/`, data);
      return response.data;
    },

    delete: async (id) => {
      await api.delete(`/financas/reservas/${id}/`);
    },
  },

  // =========================
  // --- INVESTIMENTOS ---
  // =========================
  investimentos: {
    getAll: async () => {
      const response = await api.get('/financas/investimentos/');
      return response.data;
    },

    getById: async (id) => {
      const response = await api.get(`/financas/investimentos/${id}/`);
      return response.data;
    },

    create: async (data) => {
      const response = await api.post('/financas/investimentos/', data);
      return response.data;
    },

    update: async (id, data) => {
      const response = await api.put(`/financas/investimentos/${id}/`, data);
      return response.data;
    },

    delete: async (id) => {
      await api.delete(`/financas/investimentos/${id}/`);
    },
  },
};

export default financasService;