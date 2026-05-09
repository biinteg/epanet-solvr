# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
from epyt import epanet
# pyrefly: ignore [missing-import]
import pandas as pd
from modules.helpers import (
    MAX_HEADLOSS_M_PER_KM,
    MAX_VELOCITY_MS,
    MIN_VELOCITY_MS,
    warnai_status_solver,
)


def run_auto_solver(tmp_path):
    st.write(
        "Optimasi diameter otomatis berdasarkan "
        f"Permen PU No. 18/PRT/M/2007: kecepatan {MIN_VELOCITY_MS}-{MAX_VELOCITY_MS} m/s "
        f"dan headloss <= {MAX_HEADLOSS_M_PER_KM} m/km."
    )

    d = None
    try:
        d = epanet(tmp_path)
        link_ids = d.getLinkNameID()
        diameter_awal = d.getLinkDiameter()

        standar_pipa = [50, 75, 100, 150, 200, 250, 300, 400, 500, 600, 800]

        # Iterasi optimasi
        for iterasi in range(5):
            st.info(f"Iterasi optimasi {iterasi+1}/5")

            d.openHydraulicAnalysis()
            d.runHydraulicAnalysis()
            d.closeHydraulicAnalysis()

            velocity = d.getLinkVelocity()
            headloss = d.getLinkHeadloss()

            for i in range(len(link_ids)):
                v = abs(velocity[i])
                h = abs(headloss[i])
                d_now = d.getLinkDiameter(i + 1)
                d_new = d_now

                if 0.001 < v < MIN_VELOCITY_MS:
                    kandidat = [x for x in standar_pipa if x < d_now]
                    if kandidat:
                        d_new = max(kandidat)
                elif v > MAX_VELOCITY_MS or h > MAX_HEADLOSS_M_PER_KM:
                    kandidat = [x for x in standar_pipa if x > d_now]
                    if kandidat:
                        d_new = min(kandidat)

                if d_new != d_now:
                    d.setLinkDiameter(i + 1, d_new)

        # Run final
        d.openHydraulicAnalysis()
        d.runHydraulicAnalysis()
        d.closeHydraulicAnalysis()

        final_velocity = d.getLinkVelocity()
        final_headloss = d.getLinkHeadloss()

        hasil = []
        berubah = 0
        patuh = 0

        for i in range(len(link_ids)):
            awal = diameter_awal[i]
            akhir = d.getLinkDiameter(i + 1)
            v = abs(final_velocity[i])
            h = abs(final_headloss[i])
            sesuai_permen = MIN_VELOCITY_MS <= v <= MAX_VELOCITY_MS and h <= MAX_HEADLOSS_M_PER_KM

            if akhir > awal:
                status = "Diperbesar"
            elif akhir < awal:
                status = "Diperkecil"
            else:
                status = "Tetap"

            if awal != akhir:
                berubah += 1
            if sesuai_permen:
                patuh += 1

            hasil.append({
                "ID Pipa": link_ids[i],
                "Diameter Awal": f"{awal:.0f} mm",
                "Diameter Baru": f"{akhir:.0f} mm",
                "Velocity": f"{v:.3f} m/s",
                "Headloss": f"{h:.3f} m/km",
                "Status Optimasi": status,
                "Status Permen PU": "Aman" if sesuai_permen else "Tidak Aman"
            })

        df = pd.DataFrame(hasil)

        st.markdown("### Ringkasan Optimasi")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Pipa", len(link_ids))
        c2.metric("Diubah", berubah)
        c3.metric("Pipa Sesuai", f"{patuh}/{len(link_ids)}")

        st.dataframe(
            df.style.map(warnai_status_solver, subset=["Status Optimasi"]),
            use_container_width=True,
            height=400
        )

        # Download hasil
        new_inp = tmp_path.replace(".inp", "_optimized.inp")
        d.saveInputFile(new_inp)

        with open(new_inp, "rb") as file:
            st.download_button(
                "Unduh File Optimasi",
                data=file,
                file_name="Jaringan_Optimasi.inp",
                mime="text/plain"
            )

    finally:
        if d:
            d.unload()
