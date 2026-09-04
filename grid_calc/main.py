import pandapower as pp


def create_grid():
    """Maak een eenvoudige pandapower grid-template."""
    net = pp.create_empty_network(name="Voorbeeld grid")

    k1 = pp.create_bus(net, vn_kv=150, name="K1")
    k2 = pp.create_bus(net, vn_kv=10, name="K2")
    k3 = pp.create_bus(net, vn_kv=10, name="K3")

    pp.create_ext_grid(
        net,
        bus=k1,
        vm_pu=1.0,
        s_sc_max_mva=10392,
        rx_max=0,
        name="150 kV Grid",
    )

    pp.create_transformer_from_parameters(
        net,
        hv_bus=k1,
        lv_bus=k2,
        sn_mva=50,
        vn_hv_kv=150,
        vn_lv_kv=10,
        vk_percent=20,
        vkr_percent=0.04,
        pfe_kw=20000,
        i0_percent=0,
        shift_degree=150,
        name="T1",
    )
    length_km = 5
    r_ohm_per_km = 0.621 / length_km
    x_ohm_per_km = 0.475 / length_km
    # 1.8 µF total -> nF/km
    c_nf_per_km = 1.8e3 / length_km

    pp.create_line_from_parameters(
        net,
        from_bus=k2,
        to_bus=k3,
        length_km=5,
        r_ohm_per_km=r_ohm_per_km,
        x_ohm_per_km=x_ohm_per_km,
        c_nf_per_km=c_nf_per_km,
        max_i_ka=1,
        name="L1",
    )

    pp.create_load(
        net,
        bus=k3,
        p_mw=2,
        q_mvar=1.5,
        name="Load",
    )
    # --------------------------------------------------
    # MOTOR
    # as asynchronous motor for short-circuit calculations
    # --------------------------------------------------
    P_mech = 2.0
    eta = 0.95
    cosphi = 0.85

    P_motor = P_mech / eta

    import math
    phi = math.acos(cosphi)
    Q_motor = P_motor * math.tan(phi)
    S_motor = P_motor / cosphi

    pp.create_sgen(
        net,
        bus=k3,
        p_mw=-P_motor,
        q_mvar=-Q_motor,
        sn_mva=S_motor,
        type="motor",
        k=5.0,
        rx=0.1,
        name="Motor"
    )
    # GENERATOR
    # power-flow and short-circuit representation
    # --------------------------------------------------
    pp.create_gen(
        net,
        bus=k3,
        p_mw=2.0 * 0.85,
        vm_pu=1.0,
        sn_mva=2.0,
        vn_kv=10.0,
        xdss_pu=0.20,
        rdss_ohm=5.0,
        cos_phi=0.85,
        name="Generator"
    )
    # --------------------------------------------------
    return net


def run_power_flow(net):
    """Voer een loadflow uit en toon de belangrijkste resultaten."""
    pp.runpp(net, numba=False)

    print("Bus resultaten:")
    print(net.res_bus[["vm_pu", "va_degree"]])

    print("\nLijn resultaten:")
    print(net.res_line[["loading_percent", "i_ka", "p_from_mw", "q_from_mvar"]])

    print("\nTransformator resultaten:")
    print(net.res_trafo[["loading_percent", "p_hv_mw", "q_hv_mvar"]])


def main():
    net = create_grid()
    run_power_flow(net)


if __name__ == "__main__":
    main()
