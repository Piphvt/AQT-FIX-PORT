<template>

    <div>
        <ModalConfirm :open="modal.confirm.open" :message="modal.confirm.message" :confirm.sync="modal.confirm.open"
            :method="handleConfirmMethod" />
        <ModalComplete :open="modal.complete.open" :message="modal.complete.message"
            :complete.sync="modal.complete.open" :method="goBack" />
        <ModalWarning :open="modal.warning.open" :message="modal.warning.message" :warning.sync="modal.warning.open" />

        <v-dialog persistent :retain-focus="false" v-model="open" v-if="data" max-width="400" max-height="300"
            content-class="rounded-xl">
            <v-card class="rounded-xl">
                <v-card-title class="card-title-center mb-7">แก้ไขรายละเอียดหุ้นของลูกค้า</v-card-title>
                <v-card-text>
                    <v-form ref="form" v-model="valid" lazy-validation>
                        <v-row>

                            <v-col cols="5" sm="11" class="pa-0 ml-4">
                                <v-menu ref="menu" v-model="menu" :close-on-content-click="false" :nudge-right="40"
                                    :return-value.sync="formData.created_date" transition="scale-transition" offset-y
                                    min-width="290px">
                                    <template v-slot:activator="{ on, attrs }">
                                        <v-text-field v-model="formattedCreatedDate" label="ข้อมูลวันที่" outlined dense
                                            readonly v-bind="attrs" v-on="on" :rules="[
                                                (v) => !!v || 'โปรดเลือกวันที่',
                                                (v) => moment(v).isValid() || 'วันที่ไม่ถูกต้อง'
                                            ]"></v-text-field>
                                    </template>
                                    <date-picker v-model="formData.created_date" no-title scrollable
                                        @input="onDateSelected" @change="onDateChange" format="YYYY-MM-DD HH:mm"
                                        type="datetime" :locale="'th'" />
                                </v-menu>
                            </v-col>

                            <v-col cols="6" sm="5" class="pa-0 mr-8 ml-4">
                                <v-autocomplete v-model="formData.customer_no" :items="customers"
                                    :item-text="item => item.text" :item-value="item => item.value"
                                    :rules="[(v) => !!v || 'โปรดกรอกรหัสสมาชิก']" label="รหัสสมาชิก" dense outlined
                                    clearable solo hide-no-data hide-details />
                            </v-col>

                            <v-col cols="6" sm="5" class="pa-0">
                                <v-select v-model="formData.type" :items="typeOptions" :item-text="item => item.text"
                                    :item-value="item => item.value" :rules="[(v) => !!v || 'โปรดเลือกซื้อ/ขาย']"
                                    label="ซื้อ/ขาย" dense outlined required>
                                    <template v-slot:item="data">
                                        <v-icon left>
                                            {{ data.item.icon }}
                                        </v-icon>
                                        {{ data.item.text }}
                                    </template>
                                </v-select>
                            </v-col>

                            <v-col cols="6" sm="5" class="pa-0 mr-8 ml-4">
                                <v-autocomplete v-model="formData.stock_no" :items="stocks"
                                    :item-text="item => item.text" :item-value="item => item.value"
                                    :rules="[(v) => !!v || 'โปรดกรอกชื่อหุ้น']" label="ชื่อหุ้น" dense outlined
                                    clearable solo hide-no-data hide-details />
                            </v-col>

                            <v-col cols="6" sm="5" class="pa-0">
                                <v-select v-model="formData.from_no" :items="fromOptions" :item-text="item => item.text"
                                    :item-value="item => item.value" :rules="[(v) => !!v || 'โปรดเลือกที่มาที่ไป']"
                                    label="ที่มาที่ไป" dense outlined required>
                                    <template v-slot:item="data">
                                        <v-icon left>
                                            {{ data.item.icon }}
                                        </v-icon>
                                        {{ data.item.text }}
                                    </template>
                                </v-select>
                            </v-col>

                            <v-col cols="6" sm="5" class="pa-0 mr-8 ml-4">
                                <v-text-field v-model="formData.price" :rules="[
                                    (v) => !!v || 'โปรดกรอกราคาที่ติด',
                                    (v) => /^[0-9]*\.?[0-9]+$/.test(v) || 'กรุณากรอกตัวเลข'
                                ]" label="ราคาที่ติด" dense outlined required />
                            </v-col>

                            <v-col cols="6" sm="5" class="pa-0">
                                <v-text-field v-model="formData.amount" :rules="[
                                    (v) => !!v || 'โปรดกรอกจำนวนที่ติด',
                                    (v) => /^[0-9]*\.?[0-9]+$/.test(v) || 'กรุณากรอกตัวเลข'
                                ]" label="จำนวนที่ติด" dense outlined required />
                            </v-col>
                        </v-row>
                    </v-form>
                </v-card-text>

                <v-card-actions class="card-title-center pa-0">
                    <v-btn @click="confirm"
                        :disabled="!valid || !hasChanges || !formData.customer_no || !formData.stock_no || !formData.price || !formData.amount || !formData.type  || !formData.from_no"
                        depressed color="#24b224" class="font-weight-medium mr-2 mb-5">
                        บันทึก
                    </v-btn>
                    <v-btn color="#e50211" @click="cancel" class="font-weight-medium mb-5">ยกเลิก
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>

</template>

<script>

import moment from 'moment';
moment.locale('th');
import DatePicker from 'vue2-datepicker';
import 'vue2-datepicker/index.css';

export default {

    props: {
        method: { type: Function },
        open: {
            required: true,
        },
        data: {
            required: true,
        },
    },

    components: {
        DatePicker,
    },

    data() {
        return {

            modal: {
                confirm: {
                    open: false,
                    message: 'ยืนยันการแก้ไขข้อมูล?',
                },
                complete: {
                    open: false,
                    message: 'แก้ไขข้อมูลสำเร็จ',
                },
                warning: {
                    open: false,
                    message: 'มีหุ้นชื่อนี้แล้ว',
                },
            },
            menu: false,
            moment,

            formData: {},
            valid: false,
            fromOptions: [],
            typeOptions: [
                { text: "ซื้อ", value: 1, icon: "mdi-cash-minus" },
                { text: "ขาย", value: 2, icon: "mdi-cash-plus" },
            ],
            originalData: {},
            customers: [],
            stocks: [],

        };
    },

    computed: {
        hasChanges() {
            const dateHasChanged = !moment(this.formData.created_date).isSame(this.originalData.created_date);
            const stockNoHasChanged = this.formData.stock_no !== this.originalData.stock_no;
            const priceHasChanged = parseFloat(this.formData.price).toFixed(2) !== parseFloat(this.originalData.price).toFixed(2);
            const amountHasChanged = parseFloat(this.formData.amount).toFixed(2) !== parseFloat(this.originalData.amount).toFixed(2);
            const fromHasChanged = this.formData.from_no !== this.originalData.from_no;
            const typeHasChanged = this.formData.type !== this.originalData.type;
            const customerHasChanged = this.formData.customer_no !== this.originalData.customer_no;
            return dateHasChanged || stockNoHasChanged || priceHasChanged || amountHasChanged || fromHasChanged || typeHasChanged || customerHasChanged;
        },
    },

    async mounted() {
        await this.fetchStockData()
    },

    mounted() {
        this.fetchCustomerData();
        this.fetchStockData();
        this.setFromOptions();

        this.formData = JSON.parse(JSON.stringify(this.data));
        this.originalData = JSON.parse(JSON.stringify(this.data));
        if (moment(this.formData.created_date).isValid()) {
            this.formattedCreatedDate = moment(this.formData.created_date).format('YYYY-MM-DD HH:mm');
        } else {
            this.formattedCreatedDate = '';
        }
        document.addEventListener('keydown', this.handleKeydown);
    },

    watch: {
        data: {
            handler(newData) {
                this.formData = JSON.parse(JSON.stringify(newData));
                this.originalData = JSON.parse(JSON.stringify(newData));
                if (moment(this.formData.created_date).isValid()) {
                    this.formattedCreatedDate = moment(this.formData.created_date).format('YYYY-MM-DD HH:mm');
                } else {
                    this.formattedCreatedDate = '';
                }
            },
            deep: true,
            immediate: true
        },
        formData: {
            handler(newFormData) {
                if (newFormData.stock_no) {
                    this.fetchStockData();
                }
            },
            deep: true,
        }
    },

    beforeDestroy() {
        document.removeEventListener('keydown', this.handleKeydown);
    },

    methods: {
        onDateSelected(date) {
            if (moment(date).isValid()) {
                this.formData.created_date = moment(date).toDate();
                this.formattedCreatedDate = moment(date).format('YYYY-MM-DD HH:mm');
            } else {
                this.formData.created_date = null;
                this.formattedCreatedDate = '';
            }
            this.menu = false;
        },

        async fetchCustomerData() {
            try {
                this.customers = await this.$store.dispatch('api/customer/getCustomer');
                this.customers = this.customers.map(customer => ({
                    value: customer.no,
                    text: customer.id,
                }));

                if (this.data && this.data.customer_no) {
                    const selectedType = this.customers.find(r => r.value === this.data.customer_no);
                    this.customers = selectedType
                        ? [selectedType, ...this.customers.filter(r => r.value !== this.data.customer_no)]
                        : this.customers;
                }
            } catch (warning) {
                console.error(warning);
            }
        },

        async fetchStockData() {
            try {
                const fetchedStocks = await this.$store.dispatch('api/stock/getStock');
                this.stocks = fetchedStocks.map(stock => ({
                    value: stock.no,
                    text: stock.stock,
                }));

                if (this.formData && this.formData.stock_no) {
                    const selectedType = this.stocks.find(r => r.value === this.formData.stock_no);
                    this.stocks = selectedType
                        ? [selectedType, ...this.stocks.filter(r => r.value !== this.formData.stock_no)]
                        : this.stocks;
                }
            } catch (warning) {
                console.error(warning);
            }
        },

        async setFromOptions() {
            try {
                this.froms = await this.$store.dispatch('api/from/getFrom');

                const fromIcons = {
                    'หุ้นเก่า': 'mdi-numeric-1',
                    'หุ้นใหม่': 'mdi-numeric-2',
                    'หุ้นแก้เกม': 'mdi-numeric-3',
                };

                const allTypes = this.froms.map(from => ({
                    value: from.no,
                    text: from.from,
                    icon: fromIcons[from.from] || 'mdi-currency-usd'
                }));

                const prioritizedTypes = ['หุ้นเก่า', 'หุ้นใหม่', 'หุ้นแก้เกม'];
                this.fromOptions = prioritizedTypes.reduce((acc, fromName) => {
                    const from = allTypes.find(r => r.text === fromName);
                    if (from) acc.push(from);
                    return acc;
                }, []).concat(allTypes.filter(r => !prioritizedTypes.includes(r.text)));

                if (this.data && this.data.from_no) {
                    const selectedType = this.fromOptions.find(r => r.value === this.data.from_no);
                    this.fromOptions = selectedType
                        ? [selectedType, ...this.fromOptions.filter(r => r.value !== this.data.from_no)]
                        : this.fromOptions;
                }
            } catch (warning) {
            }
        },

        getFromName(fromId) {
            const from = this.froms.find(f => f.no === fromId);
            return from ? from.from : 'ไม่ทราบ';
        },

        getStockName(stockID) {
            const stock = this.stocks.find(s => s.value === stockID);
            return stock ? stock.text : 'ไม่ทราบ';
        },

        getCustomerID(customerId) {
            const customer = this.customers.find(c => c.value === customerId);
            return customer ? customer.text : 'ไม่ทราบ';
        },

        async confirm() {
            this.modal.confirm.open = true;
            await new Promise((resolve) => {
                this.$watch('modal.confirm.open', (newValue) => {
                    if (!newValue) {
                        resolve();
                    }
                });
            });

            if (!this.modal.confirm.open) {
                return;
            }
            await this.updateData();
        },

        async updateData() {
            try {
                this.formData.employee_no = this.$auth.user.no;
                this.formData.created_date = moment(this.formData.created_date).format('YYYY-MM-DD HH:mm:ss');
                const req = await this.$store.dispatch('api/transaction/updateTransaction', this.formData);
                this.modal.complete.open = true;
                this.recordLogUpdate();
            } catch (warning) {
                this.modal.warning.open = true;
                this.modal.warning.message = 'มีบางอย่างผิดปกติ';
            }
        },

        handleKeydown(event) {
            if (event.key === 'Escape') {
                this.cancel();
            }
        },

        cancel() {
            this.modal.confirm.open = false;
            this.$emit('update:edit', false);
        },

        goBack() {
            window.location.reload();
        },

        handleConfirmMethod() {
            this.modal.confirm.open = false;
            this.updateData();
        },

        recordLogUpdate() {
            const changes = [];
            const StockText = this.getStockName(this.formData.stock_no);
            const originalStockText = this.getStockName(this.originalData.stock_no);
            if (StockText !== originalStockText) {
                changes.push('ชื่อหุ้น : ' + StockText + '\n');
            }

            const fromText = this.getFromName(this.formData.from_no);
            const originalfromText = this.getFromName(this.originalData.from_no);
            if (fromText !== originalfromText) {
                changes.push('ที่มาที่ไป : ' + fromText + '\n');
            }

            if (this.formData.price !== this.originalData.price) {
                changes.push('ราคาที่ติด : ' + this.formData.price + '\n');
            }

            if (this.formData.amount !== this.originalData.amount) {
                changes.push('จำนวนที่ติด : ' + this.formData.amount + '\n');
            }

            const log = {
                customer_no: this.getCustomerID(this.originalData.customer_no),
                emp_name: this.$auth.user.fname + ' ' + this.$auth.user.lname,
                emp_email: this.$auth.user.email,
                detail: changes.join(''),
                type: 1,
                picture: this.$auth.user.picture || 'ไม่รู้จัก',
                action: 'แก้ไขข้อมูลหุ้นของลูกค้า',
                time: moment(new Date()).format('YYYY-MM-DD HH:mm:ss'),
            };
            this.$store.dispatch('api/log/addLog', log);
        },
    },
};

</script>

<style scoped>
.card-title-center {
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
}

.file-input {
    margin-bottom: 0px !important;
}

.v-card-actions {
    padding: 0 !important;
}

.v-btn {
    margin-top: 0px !important;
}
</style>