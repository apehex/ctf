class t {
    constructor() {
        this.responseOf = "",
        this.token = localStorage.getItem("adminToken")
    }
    ngOnInit() {}
    onSelectFile(n) {
        n.target.files.length > 0 && (this.video = n.target.files[0])
    }
    onSubmit() {
        if (null !== this.token) {
            const n = new FormData;
            n.append("file", this.video),
            fetch("http://internal-api.graph.htb/admin/video/upload", {
                method: "POST",
                body: n,
                headers: {
                    admintoken: this.token
                }
            }).then(r=>r.json()).then(r=>{
                this.responseOf = r.result,
                r.url && window.open(r.url)
            }
            )
        }
    }
}
