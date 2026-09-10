from pathlib import Path
import sys
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))


import demo.draw as draw
import demo.check as check
import demo.spthy as spthy
import subprocess




def main():
    log_path = "demodata/event_log.xes"
    import demodata.ltl_rules as rules
    output_image = "demodata/dfg_image.png"
    output_spthy = "demodata/process_theory.spthy"
    tamarin_command = ["tamarin-prover", "--prove", output_spthy]

    draw.make_image(log_path, output_image)

    ltl_rules = rules.ltl_rules()
    check.run_check(log_path, ltl_rules)

    spthy.build_file(log_path, output_spthy, ltl_rules)

    subprocess.run(tamarin_command, check=True)



if __name__ == "__main__":
    main()