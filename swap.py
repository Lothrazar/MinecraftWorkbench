import os

# alternately you can set a direct path such as = r"C:\Users\USER\MyFiles\mc121"
ROOT = os.path.dirname(os.path.abspath(__file__))

OLD = """tasks.named('wrapper', Wrapper).configure {
    // Define wrapper values here so as to not have to always do so when updating gradlew.properties.
    // Switching this to Wrapper.DistributionType.ALL will download the full gradle sources that comes with
    // documentation attached on cursor hover of gradle classes and methods. However, this comes with increased
    // file size for Gradle. If you do switch this to ALL, run the Gradle wrapper task twice afterwards.
    // (Verify by checking gradle/wrapper/gradle-wrapper.properties to see if distributionUrl now points to `-all`)
    distributionType = Wrapper.DistributionType.BIN
}"""

NEW = """if (project == rootProject) {
tasks.named('wrapper', Wrapper).configure {
    // Define wrapper values here so as to not have to always do so when updating gradlew.properties.
    // Switching this to Wrapper.DistributionType.ALL will download the full gradle sources that comes with
    // documentation attached on cursor hover of gradle classes and methods. However, this comes with increased
    // file size for Gradle. If you do switch this to ALL, run the Gradle wrapper task twice afterwards.
    // (Verify by checking gradle/wrapper/gradle-wrapper.properties to see if distributionUrl now points to `-all`)
    distributionType = Wrapper.DistributionType.BIN
}
}"""

for mod in os.listdir(ROOT):
    build_gradle = os.path.join(ROOT, mod, "build.gradle")
    if not os.path.isfile(build_gradle):
        continue
    content = open(build_gradle, encoding="utf-8").read()
    if OLD in content:
        open(build_gradle, "w", encoding="utf-8").write(content.replace(OLD, NEW))
        print(f"  fixed: {mod}")
    else:
        print(f"skipped: {mod} (block not found)")

        