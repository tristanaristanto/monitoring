// GANTI DENGAN KUNCI SUPABASE LU!
const SUPABASE_URL = "https://bytgqkpcjxpjbzhkwfrf.supabase.co"; 
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ5dGdxa3BjanhwamJ6aGt3ZnJmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM4ODM0NjUsImV4cCI6MjA3OTQ1OTQ2NX0.mTNDUORV26iG_q6c-t6m-FTUIZj5mE1u2asd3Z3j1gw"; 

const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// --- 1. FUNGSI FETCH DATA UTAMA ---
async function getLatestMachineData() {
    // Meminta semua data yang dikirim oleh script Python
    let { data: readings, error } = await supabase
        .from('machine_readings')
        .select('*') 
        .order('created_at', { ascending: false });

    if (error) {
        console.error('Error fetching data:', error);
        return;
    }
    
    // Filter data, ambil yang paling baru per machine_id
    const latestData = {};
    readings.forEach(row => {
        if (!latestData[row.machine_id]) {
            latestData[row.machine_id] = row;
        }
    });

    renderRealTimeTable(Object.values(latestData));
}

// --- 2. RENDERING TABEL REAL-TIME (MENU A) ---
function renderRealTimeTable(data) {
    const tableBody = document.getElementById('machine-data-body');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    data.sort((a, b) => a.machine_id - b.machine_id);

    data.forEach(machine => {
        // Asumsi Biaya masih 1500 per kWh
        const cost = (machine.energy_total_kwh * 1500).toLocaleString('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 });
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>#${machine.machine_id}</td>
            <td>${machine.voltage ? machine.voltage.toFixed(1) : '-'}</td>
            <td>${machine.current ? machine.current.toFixed(1) : '-'}</td>
            <td>${machine.power_kw ? machine.power_kw.toFixed(2) : '-'}</td>
            <td>${machine.power_q ? machine.power_q.toFixed(2) : '-'}</td>
            <td>${machine.power_s ? machine.power_s.toFixed(2) : '-'}</td>
            <td>${machine.pf ? machine.pf.toFixed(2) : '-'}</td>
            <td>${machine.frequency ? machine.frequency.toFixed(1) : '-'}</td>
            <td>${machine.energy_total_kwh ? machine.energy_total_kwh.toLocaleString('id-ID') : '-'}</td>
            <td>${cost}</td>
            <td>${machine.status || '-'}</td>
            <td>${machine.op_time || '-'}</td>
        `;
        tableBody.appendChild(row);
    });
}

// --- 3. LOGIKA CONTROL & TARIF (MENU B & D) ---
async function saveTariff() {
    const newPrice = document.getElementById('input-tarif-harian').value;
    const { error } = await supabase
        .from('tariff_config')
        .update({ price_per_kwh: parseFloat(newPrice) })
        .eq('id', 1); // Asumsi ID konfigurasi adalah 1
    if (!error) alert(`Harga tarif baru (Rp ${newPrice}) berhasil disimpan!`);
}

async function toggleSystem() {
    const isChecked = document.getElementById('system-toggle').checked;
    const { error } = await supabase
        .from('tariff_config')
        .update({ system_on: isChecked }) 
        .eq('id', 1);
    if (!error) console.log(`Perintah sukses: Sistem ${isChecked ? 'ON' : 'OFF'}`);
}


// --- 4. ROUTING APLIKASI (The Glue) ---
// Fungsi ini harus memuat konten HTML dari file/string yang berbeda
function loadContent(menuId) {
    const contentDiv = document.getElementById('content');
    let htmlContent = '';
    
    // Asumsi lu sudah membagi HTML menjadi 4 file: realtime.html, tarif.html, dll.
    // Karena kita tidak bisa load file HTML lain di sini, kita akan gunakan template string:
    if (menuId === 'realtime') {
        htmlContent = realtimeHTML; // Gunakan template string untuk Menu A
        getLatestMachineData(); // Langsung panggil fetch data untuk realtime
        // Set interval untuk refresh setiap 5 detik
        setInterval(getLatestMachineData, 5000); 
    } else if (menuId === 'tarif') {
        htmlContent = tarifHTML; // Gunakan template string untuk Menu B
    } else if (menuId === 'trouble') {
        htmlContent = troubleHTML; // Gunakan template string untuk Menu C
    } else if (menuId === 'control') {
        htmlContent = controlHTML; // Gunakan template string untuk Menu D
    }
    
    contentDiv.innerHTML = htmlContent;
}


// Panggil fungsi ini saat halaman dimuat
document.addEventListener('DOMContentLoaded', () => {
    // Kita harus membuat string HTML untuk masing-masing menu agar routing bekerja
    // Dalam implementasi nyata, lu akan load file ini via fetch()
    
    // Asumsi HTML content strings sudah ada dari file HTML lu (Misal: realtimeHTML, tarifHTML)
    const realtimeHTML = `
        <div class="realtime-table-container">
            <h2>Monitoring Real-time (18 Mesin)</h2>
            <table class="realtime-table" style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Tegangan (V)</th>
                        <th>Arus (A)</th>
                        <th>Daya Aktif (kW)</th>
                        <th>Daya Reaktif (kVAR)</th>
                        <th>Daya Semu (kVA)</th>
                        <th>PF (-)</th>
                        <th>Frekuensi (Hz)</th>
                        <th>Total Energi (kWh)</th>
                        <th>Estimasi Biaya (Rp)</th>
                        <th>Status</th>
                        <th>Waktu Operasi (Jam)</th>
                    </tr>
                </thead>
                <tbody id="machine-data-body">
                    <tr><td colspan="12" style="text-align: center;">Memuat data...</td></tr>
                </tbody>
            </table>
        </div>`;

    const tarifHTML = `<div class="tariff-form-container">... (HTML Menu B) ...</div>`;
    const troubleHTML = `<div class="trouble-section">... (HTML Menu C) ...</div>`;
    const controlHTML = `<div class="control-panel">... (HTML Menu D) ...</div>`;

    // Untuk simulasi ini, kita langsung panggil loadContent
    loadContent('realtime');
});
