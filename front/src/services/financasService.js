import api from '@/services/APIService';

const financasService = {

  // =========================
  // --- CATEGORIAS ---
  // =========================
  categorias: {

    getAll: async () => {
      const response = await api.get('/financas/categorias/');
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
  },

  // =========================
  // --- MOVIMENTAÇÕES ---
  // =========================
  movimentacoes: {

    getAll: async () => {
      const response = await api.get('/financas/movimentacoes/');
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
      const response = await api.get(`/financas/movimentacoes/${id}/`);
      return response.data;
    },

    create: async (data) => {
      const response = await api.post('/financas/movimentacoes/', data);
      return response.data;
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
  },
};

export default financasService;