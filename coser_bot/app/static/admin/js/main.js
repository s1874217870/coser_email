// 管理后台主要JavaScript文件

const app = Vue.createApp({
    data() {
        return {
            currentPage: 'dashboard',
            loading: false,
            error: null,
            // 分页
            pagination: {
                current: 1,
                pageSize: 10,
                total: 0
            },
            // 搜索防抖
            searchTimeout: null,
            // 群组管理
            groupMembers: [],
            bannedMembers: [],
            selectedMembers: [],
            memberSearchQuery: '',
            // 仪表盘数据
            statistics: {
                totalUsers: 0,
                activeUsers: 0,
                totalPoints: 0,
                dailyCheckins: 0
            },
            // 用户管理
            users: [],
            userSearchQuery: '',
            selectedUsers: [],
            // 黑名单管理
            blacklist: [],
            // 多语言管理
            translations: {},
            // 安全日志
            logs: [],
            logFilters: {
                startDate: '',
                endDate: '',
                level: ''
            }
        }
    },
    methods: {
        // 页面导航
        async navigate(page) {
            this.currentPage = page;
            this.error = null;
            await this.loadPageData(page);
        },
        
        // 加载页面数据
        async loadPageData(page) {
            this.loading = true;
            try {
                switch (page) {
                    case 'dashboard':
                        await this.loadDashboard();
                        break;
                    case 'users':
                        await this.loadUsers();
                        break;
                    case 'blacklist':
                        await this.loadBlacklist();
                        break;
                    case 'translations':
                        await this.loadTranslations();
                        break;
                    case 'logs':
                        await this.loadLogs();
                        break;
                }
            } catch (err) {
                this.error = err.message;
            } finally {
                this.loading = false;
            }
        },
        
        // 仪表盘数据
        async loadDashboard() {
            const response = await axios.get('/admin/statistics/overview');
            this.statistics = response.data;
        },
        
        // 用户管理
        async loadUsers() {
            const response = await axios.get(
                `/admin/users?page=${this.pagination.current}&pageSize=${this.pagination.pageSize}`
            );
            this.users = response.data.items;
            this.pagination.total = response.data.total;
        },
        
        async searchUsers() {
            if (this.searchTimeout) {
                clearTimeout(this.searchTimeout);
            }
            
            this.searchTimeout = setTimeout(async () => {
                if (!this.userSearchQuery) {
                    await this.loadUsers();
                    return;
                }
                const response = await axios.get(
                    `/admin/users/search?q=${this.userSearchQuery}&page=${this.pagination.current}&pageSize=${this.pagination.pageSize}`
                );
                this.users = response.data.items;
                this.pagination.total = response.data.total;
            }, 300);
        },
        
        async banUser(userId) {
            const reason = prompt('请输入封禁原因：');
            if (!reason) return;
            
            try {
                await axios.post(`/admin/users/${userId}/ban`, { reason });
                await this.loadUsers();
            } catch (err) {
                this.error = err.message;
            }
        },
        
        // 群组管理
        async loadGroupMembers(chatId) {
            const response = await axios.get(`/admin/groups/${chatId}/members`);
            this.groupMembers = response.data;
        },
        
        async loadBannedMembers(chatId) {
            const response = await axios.get(`/admin/groups/${chatId}/banned`);
            this.bannedMembers = response.data;
        },
        
        async updateMemberPermissions(chatId, userId, permissions) {
            try {
                await axios.put(`/admin/groups/${chatId}/members/${userId}/permissions`, { permissions });
                await this.loadGroupMembers(chatId);
            } catch (err) {
                this.error = err.message;
            }
        },
        
        async kickMember(chatId, userId) {
            const reason = prompt('请输入踢出原因：');
            if (!reason) return;
            
            try {
                await axios.post(`/admin/groups/${chatId}/members/${userId}/kick`, { reason });
                await this.loadGroupMembers(chatId);
            } catch (err) {
                this.error = err.message;
            }
        },
        
        async banMember(chatId, userId) {
            const reason = prompt('请输入封禁原因：');
            if (!reason) return;
            
            try {
                await axios.post(`/admin/groups/${chatId}/members/${userId}/ban`, { reason });
                await this.loadGroupMembers(chatId);
                await this.loadBannedMembers(chatId);
            } catch (err) {
                this.error = err.message;
            }
        },
        
        async unbanMember(chatId, userId) {
            if (!confirm('确定要解封此用户吗？')) return;
            
            try {
                await axios.post(`/admin/groups/${chatId}/members/${userId}/unban`);
                await this.loadBannedMembers(chatId);
            } catch (err) {
                this.error = err.message;
            }
        },
        
        // 黑名单管理
        async loadBlacklist() {
            const response = await axios.get('/admin/blacklist');
            this.blacklist = response.data;
        },
        
        async addToBlacklist(email) {
            const reason = prompt('请输入加入黑名单的原因：');
            if (!reason) return;
            
            try {
                await axios.post(`/admin/blacklist/${email}`, { reason });
                await this.loadBlacklist();
            } catch (err) {
                this.error = err.message;
            }
        },
        
        async removeFromBlacklist(email) {
            if (!confirm('确定要从黑名单中移除此邮箱吗？')) return;
            
            try {
                await axios.delete(`/admin/blacklist/${email}`);
                await this.loadBlacklist();
            } catch (err) {
                this.error = err.message;
            }
        },
        
        // 多语言管理
        async loadTranslations() {
            const response = await axios.get('/admin/translations');
            this.translations = response.data;
        },
        
        async updateTranslation(lang, key, value) {
            try {
                await axios.put(`/admin/translations/${lang}/${key}`, { value });
                await this.loadTranslations();
            } catch (err) {
                this.error = err.message;
            }
        },
        
        // 安全日志
        async loadLogs() {
            const params = new URLSearchParams(this.logFilters);
            const response = await axios.get(`/admin/logs?${params}`);
            this.logs = response.data;
        },
        
        // 批量操作
        async batchOperation(operation) {
            if (!this.selectedUsers.length) {
                alert('请先选择用户');
                return;
            }
            
            let confirmMessage = '';
            switch (operation) {
                case 'ban':
                    confirmMessage = '确定要封禁选中的用户吗？';
                    break;
                case 'unban':
                    confirmMessage = '确定要解封选中的用户吗？';
                    break;
                case 'delete':
                    confirmMessage = '确定要删除选中的用户吗？此操作不可恢复！';
                    break;
                default:
                    return;
            }
            
            if (!confirm(confirmMessage)) {
                return;
            }
            
            try {
                await axios.post('/admin/users/batch', {
                    operation,
                    userIds: this.selectedUsers
                });
                await this.loadUsers();
                this.selectedUsers = [];
            } catch (err) {
                this.error = err.message;
            }
        }
    },
    computed: {
        totalPages() {
            return Math.ceil(this.pagination.total / this.pagination.pageSize);
        }
    },
    
    methods: {
        // 格式化日期
        formatDate(date) {
            if (!date) return '-';
            return new Date(date).toLocaleString();
        },
        
        // 获取日志级别样式
        getLevelClass(level) {
            const classes = {
                info: 'badge bg-info',
                warning: 'badge bg-warning',
                error: 'badge bg-danger'
            };
            return classes[level] || 'badge bg-secondary';
        },
        
        // 分页切换
        async changePage(page) {
            if (page < 1 || page > this.totalPages) return;
            this.pagination.current = page;
            await this.loadPageData(this.currentPage);
        },
        
        // 批量操作
        async batchOperation(operation, items) {
            if (!items || !items.length) {
                this.$message.warning('请先选择项目');
                return;
            }
            
            try {
                await axios.post(`/admin/batch/${operation}`, {
                    items: items
                });
                await this.loadPageData(this.currentPage);
                this.$message.success('操作成功');
            } catch (err) {
                this.$message.error(err.message);
            }
        }
    },
    
    mounted() {
        // 初始加载仪表盘
        this.loadPageData('dashboard');
        
        // 监听路由变化
        window.addEventListener('hashchange', () => {
            const page = window.location.hash.slice(1) || 'dashboard';
            this.navigate(page);
        });
    }
});

app.mount('#app');
