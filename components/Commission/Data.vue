<template>
    <v-dialog v-model="dialog" max-width="500px">
        <v-card>
            <div>
                <ModalConfirm :method="handleConfirm" :open="modalConfirmOpen"
                    @update:confirm="modalConfirmOpen = false" />
                <ModalComplete :open="modal.complete.open" :message="modal.complete.message"
                    :complete.sync="modal.complete.open" :method="goBack" />
                <ModalError :open="modal.error.open" :message="modal.error.message" :error.sync="modal.error.open" />
                <CommissionCreate :open="createCommissionOpen" @update:open="createCommissionOpen = false" />
                <CommissionEdit :open="editCommission" :data="editAllData" @update:edit="editCommission = false" />
            </div>
            <v-card-title class="d-flex justify-center">
                <v-icon justify="center" class="mr-3" size="40" color="#85d7df">mdi-credit-card</v-icon>
                <span class="headline">ข้อมูลค่าธรรมเนียม</span>
            </v-card-title>
            <v-card-text>
                <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
                    <v-btn @click="createCommissionOpen = true" style="font-size: 1.5 rem; margin-left: auto;" color="#24b224">
                        <v-icon left>mdi-credit-card-plus</v-icon> เพิ่ม
                    </v-btn>
                </div>
                <v-data-table :headers="headers" :items="commissions" item-value="no" item-key="no" :items-per-page="5">
                    <template v-slot:item.employee_no="{ item }">
                        <td class="text-center">{{ getEmployeeName(item.employee_no) }}</td>
                    </template>
                    <template v-slot:item.updated_date="{ item }">
                        <td class="text-center">{{ formatDateTime(item.updated_date) }}</td>
                    </template>
                    <template v-slot:item.commission="{ item }">
                        <td class="text-center">{{ item.commission }}</td>
                    </template>
                    <template v-slot:item.detail="{ item }">
                        <div class="text-center">
                            <v-menu offset-y>
                                <template v-slot:activator="{ on, attrs }">
                                    <v-icon v-bind="attrs" v-on="on" color="#85d7df">mdi-dots-vertical</v-icon>
                                </template>
                                <v-list class="custom-list">
                                    <v-list-item @click="openEditStock(item)" class="custom-list-item">
                                        <v-list-item-icon style="margin-right: 4px;">
                                            <v-icon class="icon-tab" color="#ffc800">mdi-pencil</v-icon>
                                        </v-list-item-icon>
                                        <v-list-item-content style="font-size: 0.8rem;">แก้ไข</v-list-item-content>
                                    </v-list-item>
                                    <v-list-item @click="showConfirmDialog('delete', item)" class="custom-list-item">
                                        <v-list-item-icon style="margin-right: 4px;">
                                            <v-icon class="icon-tab" color="#e50211">mdi-delete</v-icon>
                                        </v-list-item-icon>
                                        <v-list-item-content style="font-size: 0.8rem;">ลบ</v-list-item-content>
                                    </v-list-item>
                                </v-list>
                            </v-menu>
                        </div>
                    </template>
                </v-data-table>
            </v-card-text>
            <div class="text-center">
                <v-btn @click="dialog = false" class="mb-4" color="#e50211">ปิด</v-btn>
            </div>
        </v-card>
    </v-dialog>
</template>

<script>
import moment from 'moment-timezone';
import 'moment/locale/th';

export default {
    props: {
        value: Boolean,
    },

    data() {
        return {
            modal: {
                error: {
                    open: false,
                    message: '',
                },
                confirm: {
                    open: false,
                },
                complete: {
                    open: false,
                    message: '',
                },
            },

            commissions: [],
            employees: [],

            currentAction: '',
            currentItem: null,
            modalConfirmOpen: false,

            createCommissionOpen: false,

            editAllData: {},
            editCommission: false,

            headers: [
                { text: 'ข้อมูลวันที่', value: 'updated_date', align: 'center', cellClass: 'text-center' },
                { text: 'ค่าธรรมเนียม', value: 'commission', sortable: false, align: 'center', cellClass: 'text-center' },
                { text: 'ทำรายการโดย', value: 'employee_no', sortable: false, align: 'center', cellClass: 'text-center' },
                { text: '', value: 'detail', sortable: false, align: 'center', cellClass: 'text-center' },
            ],

            dialog: this.value,
        };
    },

    watch: {
        value(newValue) {
            this.dialog = newValue;
        },
        dialog(newValue) {
            this.$emit('input', newValue);
        },
    },

    async mounted() {
        await this.fetchCommissionData();
        await this.fetchEmployeeData();
    },

    methods: {
        openEditStock(commission) {
            this.editAllData = commission;
            this.editCommission = true;
        },

        goBack() {
            window.location.reload();
        },

        showConfirmDialog(action, item) {
            this.currentAction = action;
            this.currentItem = item;
            this.modalConfirmOpen = true;
        },

        async handleConfirm() {
            if (this.currentAction === 'delete') {
                try {
                    await this.$store.dispatch('api/commission/deleteCommission', this.currentItem.no);
                    this.modal.complete.message = 'ลบค่าธรรมเนียมนี้เรียบร้อยแล้ว';
                    this.modal.complete.open = true;
                    this.recordLog();
                } catch (error) {
                    this.modal.error.message = 'เกิดข้อผิดพลาดในการดำเนินการ';
                    this.modal.error.open = true;
                }
            }
            this.modalConfirmOpen = false;
        },

        async fetchCommissionData() {
            this.commissions = await this.$store.dispatch('api/commission/getCommission');
        },

        async fetchEmployeeData() {
            this.employees = await this.$store.dispatch('api/employee/getEmployee');
        },

        getEmployeeName(empId) {
            const employee = this.employees.find(e => e.no === empId);
            return employee ? employee.fname + ' ' + employee.lname : 'ไม่ทราบ';
        },

        formatDateTime(date) {
            if (moment(date).isValid()) {
                return moment(date).format('DD/MM/YYYY HH:mm');
            }
            return 'Invalid Date';
        },
        recordLog() {
            const Employee_Name = this.$auth.user.fname + ' ' + this.$auth.user.lname;
            const Employee_Email = this.$auth.user.email;
            const Employee_Picture = this.$auth.user.picture;
            const log = {
                action: 'ลบประเภทหุ้น',
                name: this.currentItem.set,
                detail: 'ไม่มีข้อมูลเพิ่มเติม',
                type: 2,
                employee_name: Employee_Name,
                employee_email: Employee_Email,
                employee_picture: Employee_Picture,
                created_date: moment(new Date()).format('YYYY-MM-DD HH:mm:ss'),
            };
            this.$store.dispatch('api/log/addLog', log);
        },
    },
};
</script>

<style>
.custom-list-item {
    padding: 0.1px 8px;
}

.custom-list {
    padding: 0.4px 2px;
}
</style>
