export const actions = {
    async getStock({ getters }, data) {
        return await this.$axios
            .get('stock', data)
            .then((res) => res.data)
    },
    async addStock({ getters }, data) {
        return await this.$axios
            .post('stock', data)
            .then((res) => res.data)
    },
    async updateStock({ getters }, data) {
        return await this.$axios
            .$put(`stock/update-stock/${data.no}`, data)
            .then((res) => res.data)
    },
    async deleteStock({ getters }, no) {
        return await this.$axios
            .delete(`stock/${no}`)
            .then((res) => res.data)
    },
    async updateStockStaff({ getters }, data) {
        return await this.$axios
            .put(`stock/update-stock-staff/${data.no}`, data)
            .then((res) => res.data)
    },
}